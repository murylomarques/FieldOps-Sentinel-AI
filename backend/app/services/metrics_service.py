from sqlalchemy.orm import Session

from app.models.metric import ModelMetric


def write_latency_metric(db: Session, latency_ms: float, drift_score: float = 0.0) -> None:
    metric = ModelMetric(
        model_name="risk_stack",
        metric_name="inference_latency_ms",
        metric_value=latency_ms,
        drift_score=drift_score,
        latency_ms=latency_ms,
    )
    db.add(metric)
    db.commit()
