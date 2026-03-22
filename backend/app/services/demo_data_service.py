from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.recommendation import Recommendation
from app.models.technician import Technician
from app.models.user import User
from app.services.agent_orchestrator import orchestrator

CITIES = [
    ("Sao Paulo", "south"),
    ("Rio de Janeiro", "east"),
    ("Belo Horizonte", "central"),
    ("Curitiba", "south"),
    ("Brasilia", "central"),
    ("Salvador", "north"),
    ("Recife", "north"),
    ("Porto Alegre", "south"),
]

SERVICE_TYPES = ["installation", "repair", "inspection", "maintenance", "emergency"]
PRIORITIES = ["low", "medium", "high", "critical"]
SKILL_BY_SERVICE = {
    "installation": "installation",
    "repair": "repair",
    "inspection": "inspection",
    "maintenance": "maintenance",
    "emergency": "emergency",
}


def _build_order(index: int) -> dict:
    city, region = random.choice(CITIES)
    service_type = random.choice(SERVICE_TYPES)
    priority = random.choices(PRIORITIES, weights=[0.2, 0.38, 0.3, 0.12], k=1)[0]

    now = datetime.now(timezone.utc)
    created_at = now - timedelta(hours=random.randint(1, 72))
    scheduled_start = now + timedelta(hours=random.randint(1, 48))
    duration = random.randint(45, 220)
    scheduled_end = scheduled_start + timedelta(minutes=duration)

    return {
        "order_id": f"ORD-DEMO-{index:05d}",
        "customer_id": f"CUST-{random.randint(10000, 99999)}",
        "city": city,
        "region": region,
        "service_type": service_type,
        "priority": priority,
        "created_at": created_at,
        "scheduled_start": scheduled_start,
        "scheduled_end": scheduled_end,
        "technician_id": f"TECH-{random.randint(1, 140):03d}",
        "technician_skill": SKILL_BY_SERVICE[service_type],
        "technician_load": random.randint(2, 12),
        "distance_km": round(random.uniform(1.2, 52.0), 2),
        "previous_reschedules": random.randint(0, 4),
        "customer_history_no_show": random.randint(0, 3),
        "rain_level": round(random.uniform(0.0, 1.0), 2),
        "traffic_level": round(random.uniform(0.0, 1.0), 2),
        "backlog_region": random.randint(12, 76),
        "sla_hours_remaining": round(random.uniform(1.0, 36.0), 2),
        "estimated_duration_minutes": duration,
    }


def seed_technicians(db: Session, total: int = 140) -> int:
    if db.query(Technician).count() > 0:
        return 0

    random.seed(7)
    created = 0
    for index in range(1, total + 1):
        city, region = random.choice(CITIES)
        skill = random.choice(list(SKILL_BY_SERVICE.values()))
        tech = Technician(
            external_code=f"TECH-{index:03d}",
            full_name=f"Technician {index:03d}",
            region=region,
            city=city,
            primary_skill=skill,
            skill_tags={"skills": [skill, "multi"]},
            status=random.choices(["available", "busy", "offline"], weights=[0.62, 0.3, 0.08], k=1)[0],
            current_load=random.randint(0, 12),
            avg_travel_minutes=round(random.uniform(14, 68), 2),
        )
        db.add(tech)
        created += 1
    db.commit()
    return created


def bootstrap_demo_operations(db: Session, n_orders: int = 180) -> dict:
    existing_orders = db.query(Order).count()
    seed_technicians(db)
    if existing_orders > 0:
        return {"seeded": 0, "reason": "orders_already_exist", "existing_orders": existing_orders}

    random.seed(42)
    generated = 0
    for idx in range(1, n_orders + 1):
        payload = _build_order(idx)
        orchestrator.upsert_order(db, payload)
        orchestrator.process_order(db, payload, request_id="SEED-DEMO", actor="system@fieldops.ai")
        generated += 1

    pending = (
        db.query(Recommendation)
        .filter(Recommendation.status.in_(["pending_human_approval", "blocked_by_policy"]))
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    dispatcher = db.query(User).filter(User.email == "dispatcher@fieldops.ai").first()

    for rec in pending[: int(len(pending) * 0.6)]:
        approve = random.random() > 0.22
        justification = (
            "Approved by dispatcher after capacity check"
            if approve
            else "Rejected due to technician travel and customer window conflict"
        )
        orchestrator.apply_human_decision(
            db,
            decision_id=rec.decision_id,
            actor="dispatcher@fieldops.ai",
            approve=approve,
            reason=justification,
            request_id="SEED-HITL",
            decided_by_user_id=dispatcher.id if dispatcher else None,
        )

    return {
        "seeded": generated,
        "pending_after_seed": db.query(Recommendation).filter(Recommendation.status == "pending_human_approval").count(),
    }
