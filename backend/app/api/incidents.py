from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.incident_note import IncidentNote
from app.models.user import User
from app.schemas.incident import IncidentNoteCreate, IncidentNoteRead, IncidentRead, IncidentUpdate

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


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> IncidentRead:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    if "assigned_analyst_id" in changes and changes["assigned_analyst_id"] is not None:
        assignee = db.get(User, changes["assigned_analyst_id"])
        if assignee is None or not assignee.is_active:
            raise HTTPException(status_code=422, detail="Assigned analyst does not exist or is inactive")
        if not {role.name for role in assignee.roles}.intersection({"Admin", "Security Analyst"}):
            raise HTTPException(status_code=422, detail="Assignee must have an analyst or admin role")

    before = {"status": incident.status, "assigned_analyst_id": incident.assigned_analyst_id}
    for field, value in changes.items():
        setattr(incident, field, value)
    incident.last_activity_at = datetime.now(timezone.utc)
    if "status" in changes:
        incident.resolved_at = incident.last_activity_at if changes["status"] in {"RESOLVED", "CLOSED"} else None
    db.add(AuditLog(
        user_id=current_user.id,
        action="incident.updated",
        resource=f"incident:{incident.id}",
        result="success",
        event_metadata={"before": before, "after": {"status": incident.status, "assigned_analyst_id": incident.assigned_analyst_id}, "fields": sorted(changes)},
    ))
    db.commit()
    db.refresh(incident)
    return IncidentRead.model_validate(incident, from_attributes=True)


@router.get("/{incident_id}/notes", response_model=list[IncidentNoteRead])
def list_incident_notes(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IncidentNoteRead]:
    if db.get(Incident, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    notes = db.scalars(
        select(IncidentNote).where(IncidentNote.incident_id == incident_id).order_by(IncidentNote.created_at.asc())
    ).all()
    return [IncidentNoteRead.model_validate(note, from_attributes=True) for note in notes]


@router.post("/{incident_id}/notes", response_model=IncidentNoteRead, status_code=201)
def add_incident_note(
    incident_id: int,
    payload: IncidentNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> IncidentNoteRead:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    now = datetime.now(timezone.utc)
    note = IncidentNote(incident_id=incident_id, author_user_id=current_user.id, body=payload.body.strip(), created_at=now)
    if not note.body:
        raise HTTPException(status_code=422, detail="Incident note cannot be blank")
    incident.last_activity_at = now
    db.add(note)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="incident.note_added",
        resource=f"incident:{incident_id}",
        result="success",
        event_metadata={"note_id": note.id},
    ))
    db.commit()
    db.refresh(note)
    return IncidentNoteRead.model_validate(note, from_attributes=True)
