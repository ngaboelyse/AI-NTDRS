from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database.session import get_db
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.response_action import ResponseAction
from app.models.response_action_request import ResponseActionRequest
from app.models.user import User
from app.schemas.response_action import ResponseActionRead, ResponseActionRequestCreate, ResponseActionRequestRead

router = APIRouter(prefix="/response-actions")


@router.get("/requests", response_model=list[ResponseActionRequestRead])
def list_action_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> list[ResponseActionRequestRead]:
    rows = db.scalars(select(ResponseActionRequest).order_by(ResponseActionRequest.requested_at.desc()).limit(200)).all()
    return [ResponseActionRequestRead.model_validate(row, from_attributes=True) for row in rows]


@router.post("/requests", response_model=ResponseActionRequestRead, status_code=201)
def request_action(
    payload: ResponseActionRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> ResponseActionRequestRead:
    if payload.alert_id is not None and db.get(Alert, payload.alert_id) is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if payload.incident_id is not None and db.get(Incident, payload.incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    request = ResponseActionRequest(
        **payload.model_dump(),
        requested_by_user_id=current_user.id,
        requested_at=datetime.now(timezone.utc),
        status="PENDING_APPROVAL",
    )
    db.add(request)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="response_action.requested",
        resource=f"response-action-request:{request.id}",
        result="pending_approval",
        event_metadata={"action_type": request.action_type, "alert_id": request.alert_id, "incident_id": request.incident_id},
    ))
    db.commit()
    db.refresh(request)
    return ResponseActionRequestRead.model_validate(request, from_attributes=True)


@router.post("/requests/{request_id}/approve", response_model=ResponseActionRead)
def approve_action_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
) -> ResponseActionRead:
    request = db.get(ResponseActionRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Response action request not found")
    if request.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=409, detail="Only pending requests can be approved")
    if request.requested_by_user_id == current_user.id:
        raise HTTPException(status_code=409, detail="A different administrator must approve this request")

    now = datetime.now(timezone.utc)
    action = ResponseAction(
        incident_id=request.incident_id,
        alert_id=request.alert_id,
        action_type=request.action_type,
        is_simulated=True,
        requested_by_user_id=request.requested_by_user_id,
        approved_by_user_id=current_user.id,
        details=request.details,
        executed_at=now,
        result="SIMULATED",
    )
    request.status = "APPROVED_SIMULATED"
    request.approved_by_user_id = current_user.id
    request.approved_at = now
    db.add(action)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="response_action.approved_simulation",
        resource=f"response-action:{action.id}",
        result="simulated",
        event_metadata={"request_id": request.id, "action_type": action.action_type},
    ))
    db.commit()
    db.refresh(action)
    return ResponseActionRead.model_validate(action, from_attributes=True)


@router.post("/requests/{request_id}/reject", response_model=ResponseActionRequestRead)
def reject_action_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
) -> ResponseActionRequestRead:
    request = db.get(ResponseActionRequest, request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Response action request not found")
    if request.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=409, detail="Only pending requests can be rejected")
    if request.requested_by_user_id == current_user.id:
        raise HTTPException(status_code=409, detail="A different administrator must review this request")
    request.status = "REJECTED"
    request.rejected_by_user_id = current_user.id
    request.approved_at = datetime.now(timezone.utc)
    db.add(AuditLog(
        user_id=current_user.id,
        action="response_action.rejected",
        resource=f"response-action-request:{request.id}",
        result="rejected",
        event_metadata={"action_type": request.action_type},
    ))
    db.commit()
    db.refresh(request)
    return ResponseActionRequestRead.model_validate(request, from_attributes=True)


@router.get("", response_model=list[ResponseActionRead])
def list_simulated_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin", "Security Analyst")),
) -> list[ResponseActionRead]:
    rows = db.scalars(select(ResponseAction).order_by(ResponseAction.executed_at.desc()).limit(200)).all()
    return [ResponseActionRead.model_validate(row, from_attributes=True) for row in rows]
