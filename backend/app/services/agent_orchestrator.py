from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from sqlalchemy.orm import Session

from app.agents.dispatch_recommendation_agent import DispatchRecommendationAgent
from app.agents.explainability_agent import ExplainabilityAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.policy_guard_agent import PolicyGuardAgent
from app.agents.risk_scoring_agent import RiskScoringAgent
from app.models.decision import Decision
from app.models.order import Order
from app.models.recommendation import Recommendation
from app.services.audit_service import write_audit
from app.services.metrics_service import write_latency_metric


class AgentOrchestrator:
    def __init__(self) -> None:
        self.intake = IntakeAgent()
        self.risk = RiskScoringAgent()
        self.dispatch = DispatchRecommendationAgent()
        self.policy = PolicyGuardAgent()
        self.explain = ExplainabilityAgent()

    def process_order(self, db: Session, payload: dict, request_id: str, actor: str) -> Recommendation:
        start = perf_counter()
        normalized = self.intake.run(payload)
        risk = self.risk.run(normalized)
        rec = self.dispatch.run(normalized, risk)
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
            status="blocked_by_policy" if policy["blocked"] else "pending_human_approval" if policy["requires_human_approval"] else "auto_applied",
            explanation_summary=explanation["operational_summary"],
            explanation_business=explanation["business_summary"],
            factors_json={"risk": risk["factors"]},
            policy_flags_json={"flags": policy["flags"], "blocked": policy["blocked"]},
        )
        db.add(recommendation)
        db.flush()

        decision = Decision(
            decision_id=decision_id,
            recommendation_id=recommendation.id,
            ai_decision_json={
                "risk": risk,
                "recommendation": rec,
                "policy": policy,
                "explanation": explanation,
            },
            human_decision="pending",
            final_outcome="pending",
        )
        db.add(decision)
        db.commit()
        db.refresh(recommendation)

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

    def apply_human_decision(self, db: Session, decision_id: str, actor: str, approve: bool, reason: str, request_id: str) -> Decision:
        decision = db.query(Decision).filter(Decision.decision_id == decision_id).first()
        if not decision:
            raise ValueError("Decision not found")
        decision.human_decision = "approved" if approve else "rejected"
        decision.human_reason = reason
        decision.decided_by = actor
        decision.decided_at = datetime.now(timezone.utc)
        decision.final_outcome = "approved_with_ai" if approve else "overridden_by_human"

        rec = db.query(Recommendation).filter(Recommendation.id == decision.recommendation_id).first()
        if rec:
            rec.status = "approved" if approve else "rejected"

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


orchestrator = AgentOrchestrator()
