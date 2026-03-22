from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.models.intervention_scenario import InterventionScenario
from app.models.order import Order
from app.models.order_event import OrderEvent
from app.models.recommendation import Recommendation
from app.models.risk_assessment import RiskAssessment


class ReplayService:
    def build_order_replay(self, db: Session, order_id: str) -> dict:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        risk = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.service_order_id == order.id)
            .order_by(RiskAssessment.created_at.desc())
            .first()
        )
        scenarios = (
            db.query(InterventionScenario)
            .filter(InterventionScenario.service_order_id == order.id)
            .order_by(InterventionScenario.created_at.asc())
            .all()
        )
        recommendation = (
            db.query(Recommendation)
            .filter(Recommendation.order_id == order.order_id)
            .order_by(Recommendation.created_at.desc())
            .first()
        )
        decision = None
        if recommendation:
            decision = db.query(Decision).filter(Decision.recommendation_id == recommendation.id).first()

        timeline = [
            {
                "timestamp": event.created_at,
                "event_type": event.event_type,
                "payload": event.event_payload_json,
            }
            for event in db.query(OrderEvent)
            .filter(OrderEvent.service_order_id == order.id)
            .order_by(OrderEvent.created_at.asc())
            .all()
        ]

        return {
            "order": {
                "order_id": order.order_id,
                "region": order.region,
                "city": order.city,
                "priority": order.priority,
                "status": order.status,
            },
            "risk_assessment": {
                "overall_risk_score": float(risk.overall_risk_score) if risk else None,
                "risk_delay_score": float(risk.risk_delay_score) if risk else None,
                "risk_no_show_score": float(risk.risk_no_show_score) if risk else None,
                "risk_reschedule_score": float(risk.risk_reschedule_score) if risk else None,
                "risk_sla_breach_score": float(risk.risk_sla_breach_score) if risk else None,
                "top_factors": risk.top_factors_json if risk else [],
            },
            "scenarios": [
                {
                    "scenario_code": s.scenario_code,
                    "scenario_type": s.scenario_type,
                    "feasibility_status": s.feasibility_status,
                    "projected_loss_avoided": float(s.projected_loss_avoided),
                    "optimizer_score": float(s.optimizer_score),
                }
                for s in scenarios
            ],
            "recommendation": {
                "decision_id": recommendation.decision_id if recommendation else None,
                "status": recommendation.status if recommendation else None,
                "action_type": recommendation.action_type if recommendation else None,
                "confidence": float(recommendation.confidence) if recommendation else None,
                "explanation_summary": recommendation.explanation_summary if recommendation else None,
            },
            "human_decision": {
                "decision": decision.human_decision if decision else None,
                "decided_by": decision.decided_by if decision else None,
                "justification": decision.human_reason if decision else None,
                "final_outcome": decision.final_outcome if decision else None,
            },
            "timeline": timeline,
        }


replay_service = ReplayService()
