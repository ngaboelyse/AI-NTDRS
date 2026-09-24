from datetime import datetime

from pydantic import BaseModel


class AlertRead(BaseModel):
    id: int
    alert_id: str
    source_ip: str
    destination_ip: str
    protocol: str
    threat_category: str
    risk_score: float
    severity: str
    detection_reason: str
    model_confidence: float | None = None
    status: str
    analyst_notes: str | None = None
    recommended_action: str | None = None
    resolution_time: datetime | None = None
