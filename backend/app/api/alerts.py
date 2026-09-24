from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.models.audit_log import AuditLog
from app.models.user import User
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertRead, AlertUpdate

router = APIRouter(prefix="/alerts")


@router.get("", response_model=list[AlertRead])
def list_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    threat_category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AlertRead]:
    query = select(Alert)
    
    filters = []
    if severity:
        filters.append(Alert.severity == severity.upper())
    if status:
        filters.append(Alert.status == status.upper())
    if threat_category:
        filters.append(Alert.threat_category.ilike(f"%{threat_category}%"))
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Alert.id.desc()).offset(skip).limit(limit)
    alerts = db.scalars(query).all()
    return [AlertRead.model_validate(alert, from_attributes=True) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> AlertRead:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertRead.model_validate(alert, from_attributes=True)


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> AlertRead:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    if "assigned_analyst_id" in changes and changes["assigned_analyst_id"] is not None:
        assignee = db.get(User, changes["assigned_analyst_id"])
        if assignee is None or not assignee.is_active:
            raise HTTPException(status_code=422, detail="Assigned analyst does not exist or is inactive")
        if not {role.name for role in assignee.roles}.intersection({"Admin", "Security Analyst"}):
            raise HTTPException(status_code=422, detail="Assignee must have an analyst or admin role")

    before = {"status": alert.status, "assigned_analyst_id": alert.assigned_analyst_id}
    for field, value in changes.items():
        setattr(alert, field, value)
    if "status" in changes:
        alert.resolution_time = datetime.now(timezone.utc) if changes["status"] in {"RESOLVED", "FALSE_POSITIVE"} else None
    db.add(AuditLog(
        user_id=current_user.id,
        action="alert.updated",
        resource=f"alert:{alert.id}",
        result="success",
        event_metadata={"before": before, "after": {"status": alert.status, "assigned_analyst_id": alert.assigned_analyst_id}, "fields": sorted(changes)},
    ))
    db.commit()
    db.refresh(alert)
    return AlertRead.model_validate(alert, from_attributes=True)
