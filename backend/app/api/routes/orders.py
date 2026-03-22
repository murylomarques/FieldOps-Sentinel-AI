from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.intervention_scenario import InterventionScenario
from app.models.order import Order
from app.models.order_event import OrderEvent
from app.models.recommendation import Recommendation
from app.models.risk_assessment import RiskAssessment
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.agent_orchestrator import orchestrator
from app.services.demo_data_service import bootstrap_demo_operations

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut)
def create_order(
    request: Request,
    payload: OrderCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> OrderOut:
    order = orchestrator.upsert_order(db, payload.model_dump())
    orchestrator.process_order(
        db,
        payload.model_dump(),
        request_id=getattr(request.state, "request_id", "n/a"),
        actor=_current_user.email,
    )
    return order


@router.post("/bulk-seed")
def bulk_seed(
    rows: int = Query(default=120, ge=1, le=2000),
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("manager")),
) -> dict:
    result = bootstrap_demo_operations(db, n_orders=rows)
    return {"status": "ok", **result}


@router.get("", response_model=list[OrderOut])
def list_orders(
    city: str | None = None,
    region: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    technician_id: str | None = None,
    risk_band: str | None = Query(default=None, description="low|medium|high|critical"),
    q: str | None = Query(default=None, description="Search by order_id"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
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
    if status:
        query = query.filter(Order.status == status)
    if technician_id:
        query = query.filter(Order.technician_id == technician_id)
    if q:
        query = query.filter(Order.order_id.ilike(f"%{q}%"))

    if risk_band:
        mapping = {
            "low": (0.0, 0.35),
            "medium": (0.35, 0.6),
            "high": (0.6, 0.8),
            "critical": (0.8, 1.01),
        }
        low, high = mapping.get(risk_band.lower(), (0.0, 1.01))
        query = query.join(RiskAssessment, RiskAssessment.service_order_id == Order.id).filter(
            RiskAssessment.overall_risk_score >= low,
            RiskAssessment.overall_risk_score < high,
        )

    offset = (page - 1) * page_size
    return query.order_by(Order.created_at.desc()).offset(offset).limit(page_size).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> OrderOut:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/timeline")
def get_order_timeline(order_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    events = (
        db.query(OrderEvent)
        .filter(OrderEvent.service_order_id == order.id)
        .order_by(OrderEvent.created_at.asc())
        .all()
    )
    return {
        "order_id": order.order_id,
        "events": [
            {"event_type": event.event_type, "event_payload": event.event_payload_json, "created_at": event.created_at}
            for event in events
        ],
    }


@router.post("/{order_id}/score")
def score_order(
    order_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> dict:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payload = {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "city": order.city,
        "region": order.region,
        "service_type": order.service_type,
        "priority": order.priority,
        "created_at": order.created_at,
        "scheduled_start": order.scheduled_start,
        "scheduled_end": order.scheduled_end,
        "technician_id": order.technician_id,
        "technician_skill": order.technician_skill,
        "technician_load": order.technician_load,
        "distance_km": order.distance_km,
        "previous_reschedules": order.previous_reschedules,
        "customer_history_no_show": order.customer_history_no_show,
        "rain_level": order.rain_level,
        "traffic_level": order.traffic_level,
        "backlog_region": order.backlog_region,
        "sla_hours_remaining": order.sla_hours_remaining,
        "estimated_duration_minutes": order.estimated_duration_minutes,
    }
    recommendation = orchestrator.process_order(
        db,
        payload,
        request_id=getattr(request.state, "request_id", "n/a"),
        actor=current_user.email,
    )
    return {"order_id": order_id, "decision_id": recommendation.decision_id, "status": recommendation.status}


@router.get("/{order_id}/risk")
def get_order_risk(order_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> dict:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    risk = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.service_order_id == order.id)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )
    if not risk:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    return {
        "order_id": order.order_id,
        "risk_delay_score": risk.risk_delay_score,
        "risk_no_show_score": risk.risk_no_show_score,
        "risk_reschedule_score": risk.risk_reschedule_score,
        "risk_sla_breach_score": risk.risk_sla_breach_score,
        "overall_risk_score": risk.overall_risk_score,
        "top_factors": risk.top_factors_json,
        "model_version": risk.model_version,
        "created_at": risk.created_at,
    }


@router.post("/{order_id}/recommend")
def recommend_for_order(
    order_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "dispatcher")),
) -> dict:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payload = {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "city": order.city,
        "region": order.region,
        "service_type": order.service_type,
        "priority": order.priority,
        "created_at": order.created_at,
        "scheduled_start": order.scheduled_start,
        "scheduled_end": order.scheduled_end,
        "technician_id": order.technician_id,
        "technician_skill": order.technician_skill,
        "technician_load": order.technician_load,
        "distance_km": order.distance_km,
        "previous_reschedules": order.previous_reschedules,
        "customer_history_no_show": order.customer_history_no_show,
        "rain_level": order.rain_level,
        "traffic_level": order.traffic_level,
        "backlog_region": order.backlog_region,
        "sla_hours_remaining": order.sla_hours_remaining,
        "estimated_duration_minutes": order.estimated_duration_minutes,
    }

    recommendation = orchestrator.process_order(
        db,
        payload,
        request_id=getattr(request.state, "request_id", "n/a"),
        actor=current_user.email,
    )

    scenario_count = db.query(InterventionScenario).filter(InterventionScenario.service_order_id == order.id).count()
    return {
        "order_id": order.order_id,
        "decision_id": recommendation.decision_id,
        "recommendation_status": recommendation.status,
        "generated_scenarios": scenario_count,
    }
