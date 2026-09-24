from datetime import datetime

from pydantic import BaseModel


class IncidentRead(BaseModel):
    id: int
    incident_code: str
    title: str
    status: str
    summary: str | None = None
    assigned_analyst_id: int | None = None
    opened_at: datetime
    last_activity_at: datetime
    resolved_at: datetime | None = None
