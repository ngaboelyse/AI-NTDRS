from datetime import datetime

from pydantic import BaseModel


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
