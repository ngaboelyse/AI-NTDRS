from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field


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
    assigned_analyst_id: int | None = None
    analyst_notes: str | None = None
    recommended_action: str | None = None
    resolution_time: datetime | None = None


class AlertUpdate(BaseModel):
    status: Literal["NEW", "INVESTIGATING", "ESCALATED", "RESOLVED", "FALSE_POSITIVE"] | None = None
    assigned_analyst_id: int | None = None
    analyst_notes: str | None = Field(default=None, max_length=5000)
