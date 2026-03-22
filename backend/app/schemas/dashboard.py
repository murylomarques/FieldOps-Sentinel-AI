from pydantic import BaseModel


class KpiResponse(BaseModel):
    percent_orders_at_risk: float
    avg_sla_risk_score: float
    approval_rate: float
    override_rate: float
    avg_response_latency_ms: float
    projected_avoided_delays: float
    projected_backlog_reduction: float
    estimated_operational_impact: float


class RegionRiskItem(BaseModel):
    region: str
    risk_score: float
    order_count: int


class ExecutiveInsight(BaseModel):
    key_bottlenecks: list[str]
    high_risk_regions: list[str]
    technician_load_alerts: list[str]
    critical_backlog: int
    risk_orders_next_hours: int
