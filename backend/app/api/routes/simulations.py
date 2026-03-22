from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.services.audit_service import write_audit
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("/what-if")
def what_if(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager")),
) -> dict:
    result = simulation_service.run_what_if(db, payload)
    write_audit(
        db,
        request_id=getattr(request.state, "request_id", "n/a"),
        decision_id="SIMULATION",
        actor=current_user.email,
        action="simulation_executed",
        details="What-if simulation executed",
        payload={"input": payload, "result": result},
    )
    return result
