from sqlalchemy.orm import Session

from app.audit.models import AuditLogModel


def create_audit_log(
    db: Session,
    *,
    action: str,
    resource: str,
    actor_id: str | None = None,
    target_id: str | None = None,
    resource_id: str | None = None,
    details: str | None = None,
) -> AuditLogModel:
    """Create a new audit log."""

    log = AuditLogModel(
        action=action,
        resource=resource,
        actor_id=actor_id,
        target_id=target_id,
        resource_id=resource_id,
        details=details,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log