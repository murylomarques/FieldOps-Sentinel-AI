from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OverrideFeedback(Base):
    __tablename__ = "override_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(Integer, ForeignKey("recommendations.id"), index=True)
    human_decision_id: Mapped[int] = mapped_column(Integer, ForeignKey("human_decisions.id"), index=True)
    override_reason_category: Mapped[str] = mapped_column(String(80), index=True)
    override_reason_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
