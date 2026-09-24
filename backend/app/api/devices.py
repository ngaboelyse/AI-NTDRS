from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceRead

router = APIRouter(prefix="/devices")


@router.post("", response_model=DeviceRead, status_code=201)
def register_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin", "Security Analyst")),
) -> DeviceRead:
    identifier = payload.device_identifier.strip()
    device_type = payload.device_type.strip()
    if not identifier or not device_type:
        raise HTTPException(status_code=422, detail="Device identifier and type cannot be blank")
    normalized_ip = str(payload.ip_address)
    existing = db.scalar(select(Device).where(
        (Device.device_identifier == identifier) | (Device.ip_address == normalized_ip)
    ))
    if existing is not None:
        raise HTTPException(status_code=409, detail="A device with that identifier or IP address already exists")
    device = Device(
        device_identifier=identifier,
        ip_address=normalized_ip,
        hostname=payload.hostname,
        device_type=device_type,
        last_seen=datetime.now(timezone.utc),
        activity_level="normal",
        risk_score=0,
        alert_count=0,
        status="online",
    )
    db.add(device)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="device.registered",
        resource=f"device:{device.id}",
        result="success",
        event_metadata={"device_identifier": device.device_identifier},
    ))
    db.commit()
    db.refresh(device)
    return DeviceRead.model_validate(device, from_attributes=True)


@router.get("", response_model=list[DeviceRead])
def list_devices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    activity_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[DeviceRead]:
    query = select(Device)
    
    filters = []
    if status:
        filters.append(Device.status == status.lower())
    if device_type:
        filters.append(Device.device_type.ilike(device_type))
    if activity_level:
        filters.append(Device.activity_level == activity_level.lower())
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Device.risk_score.desc(), Device.device_identifier).offset(skip).limit(limit)
    devices = db.scalars(query).all()
    return [DeviceRead.model_validate(device, from_attributes=True) for device in devices]


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> DeviceRead:
    device = db.get(Device, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceRead.model_validate(device, from_attributes=True)
