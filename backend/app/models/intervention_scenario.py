from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InterventionScenario(Base):
    __tablename__ = "intervention_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), index=True)
    scenario_code: Mapped[str] = mapped_column(String(64), index=True)
    scenario_type: Mapped[str] = mapped_column(String(80))
    recommended_technician_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    recommended_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recommended_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    projected_travel_delta_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    projected_risk_reduction: Mapped[float] = mapped_column(Float, default=0.0)
    projected_cost_of_action: Mapped[float] = mapped_column(Float, default=0.0)
    projected_cost_of_inaction: Mapped[float] = mapped_column(Float, default=0.0)
    projected_loss_avoided: Mapped[float] = mapped_column(Float, default=0.0)
    feasibility_status: Mapped[str] = mapped_column(String(30), default="feasible")
    policy_flags_json: Mapped[dict] = mapped_column(JSON, default=dict)
    optimizer_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
