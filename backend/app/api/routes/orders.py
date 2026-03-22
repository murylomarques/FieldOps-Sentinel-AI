from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.agent_orchestrator import orchestrator

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def create_order(
    request: Request,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderOut:
    order = orchestrator.upsert_order(db, payload.model_dump())
    orchestrator.process_order(
        db,
        payload.model_dump(),
        request_id=getattr(request.state, "request_id", "n/a"),
        actor=current_user.email,
    )
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    city: str | None = None,
    region: str | None = None,
    priority: str | None = None,
    q: str | None = Query(default=None, description="Search by order_id"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[OrderOut]:
    query = db.query(Order)
    if city:
        query = query.filter(Order.city.ilike(f"%{city}%"))
    if region:
        query = query.filter(Order.region == region)
    if priority:
        query = query.filter(Order.priority == priority)
    if q:
        query = query.filter(Order.order_id.ilike(f"%{q}%"))
    return query.order_by(Order.created_at.desc()).limit(200).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> OrderOut:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
