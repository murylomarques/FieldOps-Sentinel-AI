from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.decision import Decision
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.recommendation import ApprovalRequest, RecommendationOut, RecommendationQueueItem
from app.services.agent_orchestrator import orchestrator

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationQueueItem])
def list_recommendations(
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[RecommendationQueueItem]:
    page = max(1, page)
    page_size = max(1, min(page_size, 200))

    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)

    return query.order_by(Recommendation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


@router.get("/queue", response_model=list[RecommendationQueueItem])
def queue(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> list[RecommendationQueueItem]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.status.in_(["pending_human_approval", "blocked_by_policy"]))
        .order_by(Recommendation.created_at.desc())
        .limit(200)
        .all()
    )


@router.get("/{recommendation_id}", response_model=RecommendationOut)
def by_id(recommendation_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> RecommendationOut:
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.get("/decision/{decision_id}")
def decision_detail(decision_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    decision = db.query(Decision).filter(Decision.decision_id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return {
        "decision_id": decision.decision_id,
        "recommendation_id": decision.recommendation_id,
        "ai_decision": decision.ai_decision_json,
        "human_decision": decision.human_decision,
        "human_reason": decision.human_reason,
        "decided_by": decision.decided_by,
        "decided_at": decision.decided_at,
        "final_outcome": decision.final_outcome,
    }


@router.post("/approve")
def approve_legacy(
    request: Request,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> dict:
    decision = orchestrator.apply_human_decision(
        db,
        decision_id=payload.decision_id,
        actor=current_user.email,
        approve=payload.approve,
        reason=payload.justification,
        request_id=getattr(request.state, "request_id", "n/a"),
        decided_by_user_id=current_user.id,
    )
    return {
        "decision_id": decision.decision_id,
        "human_decision": decision.human_decision,
        "human_reason": decision.human_reason,
        "decided_by": decision.decided_by,
        "decided_at": decision.decided_at,
        "final_outcome": decision.final_outcome,
    }


@router.post("/{recommendation_id}/approve")
def approve(
    recommendation_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> dict:
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    decision = orchestrator.apply_human_decision(
        db,
        decision_id=rec.decision_id,
        actor=current_user.email,
        approve=True,
        reason=payload.get("justification", "Approved by authorized user"),
        request_id=getattr(request.state, "request_id", "n/a"),
        decided_by_user_id=current_user.id,
    )
    return {"status": "approved", "decision_id": decision.decision_id}


@router.post("/{recommendation_id}/reject")
def reject(
    recommendation_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> dict:
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    decision = orchestrator.apply_human_decision(
        db,
        decision_id=rec.decision_id,
        actor=current_user.email,
        approve=False,
        reason=payload.get("justification", "Rejected by authorized user"),
        request_id=getattr(request.state, "request_id", "n/a"),
        decided_by_user_id=current_user.id,
    )
    return {"status": "rejected", "decision_id": decision.decision_id}
