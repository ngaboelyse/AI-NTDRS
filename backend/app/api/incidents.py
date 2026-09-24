from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentRead

router = APIRouter(prefix="/incidents")


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[IncidentRead]:
    query = select(Incident)
    
    filters = []
    if status:
        filters.append(Incident.status == status.upper())
    if severity:
        filters.append(Incident.severity == severity.upper())
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Incident.last_activity_at.desc()).offset(skip).limit(limit)
    incidents = db.scalars(query).all()
    return [IncidentRead.model_validate(incident, from_attributes=True) for incident in incidents]


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> IncidentRead:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentRead.model_validate(incident, from_attributes=True)
