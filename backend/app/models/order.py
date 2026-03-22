from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    city: Mapped[str] = mapped_column(String(120))
    region: Mapped[str] = mapped_column(String(80), index=True)
    service_type: Mapped[str] = mapped_column(String(80))
    priority: Mapped[str] = mapped_column(String(30), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    technician_id: Mapped[str] = mapped_column(String(64), index=True)
    technician_skill: Mapped[str] = mapped_column(String(80))
    technician_load: Mapped[int] = mapped_column(Integer)
    distance_km: Mapped[float] = mapped_column(Float)
    previous_reschedules: Mapped[int] = mapped_column(Integer)
    customer_history_no_show: Mapped[int] = mapped_column(Integer)
    rain_level: Mapped[float] = mapped_column(Float)
    traffic_level: Mapped[float] = mapped_column(Float)
    backlog_region: Mapped[int] = mapped_column(Integer)
    sla_hours_remaining: Mapped[float] = mapped_column(Float)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="open")
    notes: Mapped[str] = mapped_column(Text, default="")
