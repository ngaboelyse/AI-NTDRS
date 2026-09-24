from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.device import Device
from app.schemas.device import DeviceRead

router = APIRouter(prefix="/devices")


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
