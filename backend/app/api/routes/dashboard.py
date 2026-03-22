from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.agents.executive_report_agent import ExecutiveReportAgent
from app.db.session import get_db
from app.models.decision import Decision
from app.models.metric import ModelMetric
from app.models.order import Order
from app.models.recommendation import Recommendation
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
report_agent = ExecutiveReportAgent()


@router.get("/kpis")
def kpis(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    total_orders = db.query(Order).count() or 1
    at_risk = db.query(Recommendation).filter(Recommendation.impact_score >= 0.6).count()
    avg_risk = db.query(func.avg(Recommendation.impact_score)).scalar() or 0.0
    approved = db.query(Decision).filter(Decision.human_decision == "approved").count()
    rejected = db.query(Decision).filter(Decision.human_decision == "rejected").count()
    decisions = approved + rejected
    approval_rate = approved / decisions if decisions else 0.0
    override_rate = rejected / decisions if decisions else 0.0

    latency = db.query(func.avg(ModelMetric.latency_ms)).scalar() or 0.0
    projected_avoided_delays = round(at_risk * 0.42, 2)
    projected_backlog_reduction = round(min(0.35, avg_risk * 0.4) * 100, 2)
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


@router.get("/risk-by-region")
def risk_by_region(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> list[dict]:
    rows = (
        db.query(Order.region, func.avg(Recommendation.impact_score), func.count(Recommendation.id))
        .join(Recommendation, Recommendation.order_id == Order.order_id)
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
        "orders": db.query(Order).count(),
        "recommendations": db.query(Recommendation).count(),
        "decisions": db.query(Decision).count(),
        "pending_human_approval": db.query(Recommendation).filter(Recommendation.status == "pending_human_approval").count(),
        "approved": db.query(Decision).filter(Decision.human_decision == "approved").count(),
        "rejected": db.query(Decision).filter(Decision.human_decision == "rejected").count(),
    }
