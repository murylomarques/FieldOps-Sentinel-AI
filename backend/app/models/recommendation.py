from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.order_id"), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    impact_score: Mapped[float] = mapped_column(Float)
    recommended_priority: Mapped[str] = mapped_column(String(30))
    recommended_technician_id: Mapped[str] = mapped_column(String(64))
    recommended_region: Mapped[str] = mapped_column(String(80))
    recommended_window: Mapped[str] = mapped_column(String(120))
    action_type: Mapped[str] = mapped_column(String(60))
    requires_human_approval: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(40), default="pending_human_approval", index=True)
    explanation_summary: Mapped[str] = mapped_column(Text)
    explanation_business: Mapped[str] = mapped_column(Text)
    factors_json: Mapped[dict] = mapped_column(JSON)
    policy_flags_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
