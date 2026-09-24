from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead

router = APIRouter(prefix="/audit-logs")


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
) -> list[AuditLogRead]:
    audit_logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all()
    return [AuditLogRead.model_validate(item, from_attributes=True) for item in audit_logs]


@router.get("/{audit_log_id}", response_model=AuditLogRead)
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
) -> AuditLogRead:
    audit_log = db.get(AuditLog, audit_log_id)
    if audit_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return AuditLogRead.model_validate(audit_log, from_attributes=True)
