from datetime import datetime

from pydantic import BaseModel, Field, IPvAnyAddress


class DeviceCreate(BaseModel):
    device_identifier: str = Field(..., min_length=1, max_length=100)
    ip_address: IPvAnyAddress
    hostname: str | None = Field(default=None, max_length=255)
    device_type: str = Field(..., min_length=1, max_length=100)


class DeviceRead(BaseModel):
    id: int
    device_identifier: str
    ip_address: str
    hostname: str | None = None
    device_type: str
    last_seen: datetime | None = None
    activity_level: str
    risk_score: float
    alert_count: int
    status: str
