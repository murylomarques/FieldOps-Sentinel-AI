from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.replay_service import replay_service

router = APIRouter(prefix="/replay", tags=["replay"])


@router.get("/orders/{order_id}")
def replay_order(order_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    try:
        return replay_service.build_order_replay(db, order_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
