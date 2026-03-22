from datetime import datetime

from pydantic import BaseModel


class RecommendationOut(BaseModel):
    id: int
    decision_id: str
    order_id: str
    confidence: float
    impact_score: float
    recommended_priority: str
    recommended_technician_id: str
    recommended_region: str
    recommended_window: str
    action_type: str
    requires_human_approval: bool
    status: str
    explanation_summary: str
    explanation_business: str
    factors_json: dict
    policy_flags_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequest(BaseModel):
    decision_id: str
    approve: bool
    justification: str


class RecommendationQueueItem(BaseModel):
    id: int
    decision_id: str
    order_id: str
    confidence: float
    impact_score: float
    status: str
    action_type: str
    recommended_priority: str
    created_at: datetime

    model_config = {"from_attributes": True}
