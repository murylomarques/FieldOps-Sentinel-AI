from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from sqlalchemy.orm import Session

from app.agents.dispatch_recommendation_agent import DispatchRecommendationAgent
from app.agents.explainability_agent import ExplainabilityAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.policy_guard_agent import PolicyGuardAgent
from app.agents.risk_scoring_agent import RiskScoringAgent
from app.agents.scenario_generation_agent import ScenarioGenerationAgent
from app.models.decision import Decision
from app.models.human_decision import HumanDecision
from app.models.intervention_scenario import InterventionScenario
from app.models.order import Order
from app.models.order_event import OrderEvent
from app.models.override_feedback import OverrideFeedback
from app.models.recommendation import Recommendation
from app.models.risk_assessment import RiskAssessment
from app.models.technician import Technician
from app.services.audit_service import write_audit
from app.services.metrics_service import write_latency_metric


class AgentOrchestrator:
    def __init__(self) -> None:
        self.intake = IntakeAgent()
        self.risk = RiskScoringAgent()
        self.dispatch = DispatchRecommendationAgent()
        self.scenario = ScenarioGenerationAgent()
        self.optimizer = OptimizationAgent()
        self.policy = PolicyGuardAgent()
        self.explain = ExplainabilityAgent()

    def process_order(self, db: Session, payload: dict, request_id: str, actor: str) -> Recommendation:
        start = perf_counter()
        normalized = self.intake.run(payload)

        order = db.query(Order).filter(Order.order_id == normalized["order_id"]).first()
        if not order:
            order = self.upsert_order(db, normalized)

        self._emit_event(db, order.id, "order_ingested", {"order_id": order.order_id, "actor": actor})
        risk = self.risk.run(normalized)

        risk_row = RiskAssessment(
            service_order_id=order.id,
            risk_delay_score=risk["delay_risk"],
            risk_no_show_score=risk["no_show_risk"],
            risk_reschedule_score=risk["reschedule_risk"],
            risk_sla_breach_score=risk.get("sla_breach_risk", risk["overall_risk"]),
            overall_risk_score=risk["overall_risk"],
            top_factors_json={"factors": risk["factors"]},
            model_version="v1.1",
        )
        db.add(risk_row)
        db.commit()
        self._emit_event(db, order.id, "risk_scored", {"overall_risk": risk["overall_risk"]})

        technicians = self._load_technicians(db)
        order_context = normalized | {
            "projected_sla_penalty": normalized.get("projected_sla_penalty", 220.0),
            "order_value": normalized.get("order_value", 380.0),
        }

        scenarios = self.scenario.run(order_context, risk, technicians)
        scenario_rows: list[InterventionScenario] = []
        for item in scenarios:
            row_data = {
                "scenario_code": item["scenario_code"],
                "scenario_type": item["scenario_type"],
                "recommended_technician_id": item.get("recommended_technician_id"),
                "recommended_start": item.get("recommended_start"),
                "recommended_end": item.get("recommended_end"),
                "projected_travel_delta_minutes": item.get("projected_travel_delta_minutes", 0.0),
                "projected_risk_reduction": item.get("projected_risk_reduction", 0.0),
                "projected_cost_of_action": item.get("projected_cost_of_action", 0.0),
                "projected_cost_of_inaction": item.get("projected_cost_of_inaction", 0.0),
                "projected_loss_avoided": item.get("projected_loss_avoided", 0.0),
                "feasibility_status": item.get("feasibility_status", "feasible"),
                "policy_flags_json": item.get("policy_flags_json", {}),
                "optimizer_score": 0.0,
            }
            row = InterventionScenario(service_order_id=order.id, **row_data)
            db.add(row)
            scenario_rows.append(row)
        db.commit()
        self._emit_event(db, order.id, "scenarios_generated", {"count": len(scenario_rows)})

        best = self.optimizer.run(scenarios)

        rec = self.dispatch.run(normalized, risk)
        rec["recommended_technician_id"] = best.get("recommended_technician_id") or rec["recommended_technician_id"]
        rec["recommended_window"] = (
            f"{best.get('recommended_start')} to {best.get('recommended_end')}"
            if best.get("recommended_start") and best.get("recommended_end")
            else rec["recommended_window"]
        )
        rec["action_type"] = best.get("scenario_type", rec["action_type"])
        rec["projected_loss_avoided"] = best.get("projected_loss_avoided", 0.0)
        rec["projected_risk_reduction"] = best.get("projected_risk_reduction", 0.0)
        rec["projected_travel_delta_minutes"] = best.get("projected_travel_delta_minutes", 0.0)
        rec["confidence"] = min(0.99, max(rec["confidence"], 0.55 + (risk["overall_risk"] * 0.35)))
        rec["severity"] = (
            "critical"
            if risk["overall_risk"] >= 0.8
            else "high"
            if risk["overall_risk"] >= 0.65
            else "medium"
            if risk["overall_risk"] >= 0.4
            else "low"
        )

        policy = self.policy.run(normalized, rec, risk)
        explanation = self.explain.run(normalized, risk, rec, policy)

        decision_id = f"DEC-{uuid4().hex[:12].upper()}"
        recommendation = Recommendation(
            decision_id=decision_id,
            order_id=normalized["order_id"],
            confidence=rec["confidence"],
            impact_score=rec["impact_score"],
            recommended_priority=rec["recommended_priority"],
            recommended_technician_id=rec["recommended_technician_id"],
            recommended_region=rec["recommended_region"],
            recommended_window=rec["recommended_window"],
            action_type=rec["action_type"],
            requires_human_approval=policy["requires_human_approval"],
            status=(
                "blocked_by_policy"
                if policy["blocked"]
                else "pending_human_approval"
                if policy["requires_human_approval"]
                else "auto_applied"
            ),
            explanation_summary=explanation["operational_summary"],
            explanation_business=explanation["executive_summary"],
            factors_json={"risk": risk["factors"], "reason_summary": explanation["reason_summary"]},
            policy_flags_json={
                "flags": policy["flags"],
                "blocked": policy["blocked"],
                "optimizer": {
                    "scenario_code": best.get("scenario_code"),
                    "optimizer_score": best.get("optimizer_score", 0.0),
                    "projected_loss_avoided": best.get("projected_loss_avoided", 0.0),
                },
            },
        )
        db.add(recommendation)
        db.flush()

        decision_payload = self._json_safe(
            {
                "risk": risk,
                "recommendation": rec,
                "policy": policy,
                "explanation": explanation,
                "selected_scenario": best,
            }
        )
        decision = Decision(
            decision_id=decision_id,
            recommendation_id=recommendation.id,
            ai_decision_json=decision_payload,
            human_decision="pending",
            final_outcome="pending",
        )
        db.add(decision)
        db.commit()
        db.refresh(recommendation)

        self._emit_event(
            db,
            order.id,
            "recommendation_created",
            {"decision_id": decision_id, "status": recommendation.status, "scenario": best.get("scenario_code")},
        )

        latency_ms = (perf_counter() - start) * 1000
        write_latency_metric(db, latency_ms=latency_ms, drift_score=0.04)
        write_audit(
            db,
            request_id=request_id,
            decision_id=decision_id,
            actor=actor,
            action="recommendation_generated",
            details="AI recommendation created by agent pipeline",
            payload={"order_id": normalized["order_id"], "status": recommendation.status, "latency_ms": latency_ms},
        )
        return recommendation

    def upsert_order(self, db: Session, payload: dict) -> Order:
        order = db.query(Order).filter(Order.order_id == payload["order_id"]).first()
        fields = {
            "customer_id": payload["customer_id"],
            "city": payload["city"],
            "region": payload["region"],
            "service_type": payload["service_type"],
            "priority": payload["priority"],
            "created_at": payload["created_at"],
            "scheduled_start": payload["scheduled_start"],
            "scheduled_end": payload["scheduled_end"],
            "technician_id": payload["technician_id"],
            "technician_skill": payload["technician_skill"],
            "technician_load": payload["technician_load"],
            "distance_km": payload["distance_km"],
            "previous_reschedules": payload["previous_reschedules"],
            "customer_history_no_show": payload["customer_history_no_show"],
            "rain_level": payload["rain_level"],
            "traffic_level": payload["traffic_level"],
            "backlog_region": payload["backlog_region"],
            "sla_hours_remaining": payload["sla_hours_remaining"],
            "estimated_duration_minutes": payload["estimated_duration_minutes"],
        }
        if order:
            for key, value in fields.items():
                setattr(order, key, value)
        else:
            order = Order(order_id=payload["order_id"], status="open", notes="", **fields)
            db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def apply_human_decision(
        self,
        db: Session,
        decision_id: str,
        actor: str,
        approve: bool,
        reason: str,
        request_id: str,
        decided_by_user_id: int | None = None,
    ) -> Decision:
        decision = db.query(Decision).filter(Decision.decision_id == decision_id).first()
        if not decision:
            raise ValueError("Decision not found")
        decision.human_decision = "approved" if approve else "rejected"
        decision.human_reason = reason
        decision.decided_by = actor
        decision.decided_at = datetime.now(UTC)
        decision.final_outcome = "approved_with_ai" if approve else "overridden_by_human"

        rec = db.query(Recommendation).filter(Recommendation.id == decision.recommendation_id).first()
        if rec:
            rec.status = "approved" if approve else "rejected"

            human_decision = HumanDecision(
                recommendation_id=rec.id,
                decided_by_user_id=decided_by_user_id,
                decision=decision.human_decision,
                justification=reason,
            )
            db.add(human_decision)
            db.flush()

            if not approve:
                category = self._classify_override(reason)
                db.add(
                    OverrideFeedback(
                        recommendation_id=rec.id,
                        human_decision_id=human_decision.id,
                        override_reason_category=category,
                        override_reason_text=reason,
                    )
                )

            order = db.query(Order).filter(Order.order_id == rec.order_id).first()
            if order:
                self._emit_event(
                    db,
                    order.id,
                    "human_decision_recorded",
                    {
                        "decision_id": decision_id,
                        "decision": decision.human_decision,
                        "reason": reason,
                        "decided_by": actor,
                    },
                )

        db.commit()
        db.refresh(decision)
        write_audit(
            db,
            request_id=request_id,
            decision_id=decision_id,
            actor=actor,
            action="human_decision",
            details=f"Human {'approved' if approve else 'rejected'} recommendation",
            payload={"justification": reason},
        )
        return decision

    @staticmethod
    def _json_safe(value):
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: AgentOrchestrator._json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [AgentOrchestrator._json_safe(v) for v in value]
        return value

    @staticmethod
    def _classify_override(reason: str) -> str:
        text = reason.lower()
        if "policy" in text:
            return "policy_conflict"
        if "travel" in text:
            return "unrealistic_travel"
        if "customer" in text:
            return "customer_constraint"
        if "tech" in text:
            return "technician_constraint"
        if "context" in text:
            return "missing_context"
        if "trust" in text or "confidence" in text:
            return "low_trust_in_score"
        return "other"

    @staticmethod
    def _emit_event(db: Session, service_order_id: int, event_type: str, payload: dict) -> None:
        db.add(OrderEvent(service_order_id=service_order_id, event_type=event_type, event_payload_json=payload))
        db.commit()

    @staticmethod
    def _load_technicians(db: Session) -> list[dict]:
        tech_rows = db.query(Technician).all()
        return [
            {
                "external_code": tech.external_code,
                "region": tech.region,
                "status": tech.status,
                "skills": [tech.primary_skill, *list(tech.skill_tags.get("skills", []) if isinstance(tech.skill_tags, dict) else [])],
            }
            for tech in tech_rows
        ]


orchestrator = AgentOrchestrator()
