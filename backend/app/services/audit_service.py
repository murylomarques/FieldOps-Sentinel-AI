from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def write_audit(
    db: Session,
    *,
    request_id: str,
    decision_id: str,
    actor: str,
    action: str,
    details: str,
    payload: dict,
) -> None:
    log = AuditLog(
        request_id=request_id,
        decision_id=decision_id,
        actor=actor,
        action=action,
        details=details,
        payload_json=payload,
    )
    db.add(log)
    db.commit()
