from datetime import datetime
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    order_id: str = Field(min_length=3, max_length=64)
    customer_id: str
    city: str
    region: str
    service_type: str
    priority: str
    created_at: datetime
    scheduled_start: datetime
    scheduled_end: datetime
    technician_id: str
    technician_skill: str
    technician_load: int = Field(ge=0, le=24)
    distance_km: float = Field(ge=0, le=500)
    previous_reschedules: int = Field(ge=0, le=20)
    customer_history_no_show: int = Field(ge=0, le=20)
    rain_level: float = Field(ge=0, le=1)
    traffic_level: float = Field(ge=0, le=1)
    backlog_region: int = Field(ge=0, le=500)
    sla_hours_remaining: float = Field(ge=0, le=240)
    estimated_duration_minutes: int = Field(ge=10, le=600)


class OrderOut(OrderCreate):
    id: int
    status: str
    notes: str

    model_config = {"from_attributes": True}


class OrderFilter(BaseModel):
    city: str | None = None
    region: str | None = None
    priority: str | None = None
    technician_id: str | None = None
    min_sla_hours: float | None = None
    max_sla_hours: float | None = None
    q: str | None = None
