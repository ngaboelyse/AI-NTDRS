from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertRead

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
