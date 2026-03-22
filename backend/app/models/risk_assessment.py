from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), index=True)
    risk_delay_score: Mapped[float] = mapped_column(Float)
    risk_no_show_score: Mapped[float] = mapped_column(Float)
    risk_reschedule_score: Mapped[float] = mapped_column(Float)
    risk_sla_breach_score: Mapped[float] = mapped_column(Float)
    overall_risk_score: Mapped[float] = mapped_column(Float)
    top_factors_json: Mapped[dict] = mapped_column(JSON)
    model_version: Mapped[str] = mapped_column(String(40), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
