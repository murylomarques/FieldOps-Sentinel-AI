from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.agents.executive_report_agent import ExecutiveReportAgent
from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.decision import Decision
from app.models.human_decision import HumanDecision
from app.models.intervention_scenario import InterventionScenario
from app.models.metric import ModelMetric
from app.models.order import Order
from app.models.recommendation import Recommendation
from app.models.risk_assessment import RiskAssessment
from app.models.technician import Technician
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
report_agent = ExecutiveReportAgent()


def _summary_payload(db: Session) -> dict:
    total_orders = db.query(Order).count() or 1
    at_risk = db.query(RiskAssessment).filter(RiskAssessment.overall_risk_score >= 0.6).count()
    avg_risk = db.query(func.avg(RiskAssessment.risk_sla_breach_score)).scalar() or 0.0
    approved = db.query(Decision).filter(Decision.human_decision == "approved").count()
    rejected = db.query(Decision).filter(Decision.human_decision == "rejected").count()
    decisions = approved + rejected
    approval_rate = approved / decisions if decisions else 0.0
    override_rate = rejected / decisions if decisions else 0.0

    latency = db.query(func.avg(ModelMetric.latency_ms)).scalar() or 0.0
    projected_avoided_delays = round(at_risk * 0.42, 2)
    projected_backlog_reduction = round(min(0.35, float(avg_risk) * 0.4) * 100, 2)
    estimated_operational_impact = round((approval_rate * 0.6 + (1 - override_rate) * 0.4) * 100, 2)

    return {
        "percent_orders_at_risk": round((at_risk / total_orders) * 100, 2),
        "avg_sla_risk_score": round(float(avg_risk) * 100, 2),
        "approval_rate": round(approval_rate * 100, 2),
        "override_rate": round(override_rate * 100, 2),
        "avg_response_latency_ms": round(float(latency), 2),
        "projected_avoided_delays": projected_avoided_delays,
        "projected_backlog_reduction": projected_backlog_reduction,
        "estimated_operational_impact": estimated_operational_impact,
    }


@router.get("/kpis")
def kpis(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    return _summary_payload(db)


@router.get("/summary")
def summary(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    return _summary_payload(db)


@router.get("/critical-orders")
def critical_orders(limit: int = 10, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> list[dict]:
    rows = (
        db.query(Order.order_id, Order.city, Order.region, RiskAssessment.overall_risk_score, RiskAssessment.risk_sla_breach_score)
        .join(RiskAssessment, RiskAssessment.service_order_id == Order.id)
        .filter(RiskAssessment.overall_risk_score >= 0.65)
        .order_by(RiskAssessment.overall_risk_score.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    return [
        {
            "order_id": order_id,
            "city": city,
            "region": region,
            "overall_risk_score": round(float(overall), 4),
            "sla_breach_risk": round(float(sla), 4),
        }
        for order_id, city, region, overall, sla in rows
    ]


@router.get("/approval-metrics")
def approval_metrics(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    approved = db.query(Decision).filter(Decision.human_decision == "approved").count()
    rejected = db.query(Decision).filter(Decision.human_decision == "rejected").count()
    pending = db.query(Recommendation).filter(Recommendation.status == "pending_human_approval").count()
    total = approved + rejected
    return {
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "approval_rate": round((approved / total) * 100, 2) if total else 0.0,
        "override_rate": round((rejected / total) * 100, 2) if total else 0.0,
    }


@router.get("/model-monitoring")
def model_monitoring(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    latency = db.query(func.avg(ModelMetric.latency_ms)).scalar() or 0
    volume = db.query(ModelMetric).count()
    avg_metric = db.query(func.avg(ModelMetric.metric_value)).scalar() or 0
    drift = db.query(func.avg(ModelMetric.drift_score)).scalar() or 0

    score_distribution = (
        db.query(Recommendation.status, func.count(Recommendation.id))
        .group_by(Recommendation.status)
        .all()
    )

    return {
        "avg_latency_ms": round(float(latency), 2),
        "processed_volume": volume,
        "avg_score": round(float(avg_metric), 4),
        "simulated_drift": round(float(drift), 4),
        "score_distribution": [{"status": status, "count": count} for status, count in score_distribution],
    }


@router.get("/loss-prevention")
def loss_prevention(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    avoided = db.query(func.sum(InterventionScenario.projected_loss_avoided)).scalar() or 0.0
    action_cost = db.query(func.sum(InterventionScenario.projected_cost_of_action)).scalar() or 0.0
    inaction = db.query(func.sum(InterventionScenario.projected_cost_of_inaction)).scalar() or 0.0
    return {
        "projected_loss_avoided_total": round(float(avoided), 2),
        "projected_action_cost_total": round(float(action_cost), 2),
        "projected_inaction_cost_total": round(float(inaction), 2),
    }


@router.get("/risk-by-region")
def risk_by_region(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> list[dict]:
    rows = (
        db.query(Order.region, func.avg(RiskAssessment.overall_risk_score), func.count(RiskAssessment.id))
        .join(RiskAssessment, RiskAssessment.service_order_id == Order.id)
        .group_by(Order.region)
        .all()
    )
    return [
        {"region": region, "risk_score": round(float(score or 0.0) * 100, 2), "order_count": count}
        for region, score, count in rows
    ]


@router.get("/executive-insights")
def executive_insights(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    return report_agent.run(db)


@router.get("/demo-status")
def demo_status(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    return {
        "users": db.query(User).count(),
        "technicians": db.query(Technician).count(),
        "orders": db.query(Order).count(),
        "risk_assessments": db.query(RiskAssessment).count(),
        "scenarios": db.query(InterventionScenario).count(),
        "recommendations": db.query(Recommendation).count(),
        "human_decisions": db.query(HumanDecision).count(),
        "audit_logs": db.query(AuditLog).count(),
    }
