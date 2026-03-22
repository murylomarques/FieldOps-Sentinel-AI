from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.decision import Decision
from app.models.metric import ModelMetric
from app.models.recommendation import Recommendation
from app.models.user import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/models")
def model_monitoring(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    latency = db.query(func.avg(ModelMetric.latency_ms)).scalar() or 0
    volume = db.query(ModelMetric).count()
    avg_metric = db.query(func.avg(ModelMetric.metric_value)).scalar() or 0
    drift = db.query(func.avg(ModelMetric.drift_score)).scalar() or 0

    total_decisions = db.query(Decision).filter(Decision.human_decision.in_(["approved", "rejected"])) .count()
    overrides = db.query(Decision).filter(Decision.human_decision == "rejected").count()
    override_rate = (overrides / total_decisions) * 100 if total_decisions else 0

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
        "human_override_rate": round(override_rate, 2),
        "score_distribution": [{"status": status, "count": count} for status, count in score_distribution],
    }
