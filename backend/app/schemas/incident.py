from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field


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


class IncidentUpdate(BaseModel):
    status: Literal["NEW", "INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"] | None = None
    summary: str | None = Field(default=None, max_length=500)
    assigned_analyst_id: int | None = None


class IncidentNoteCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)


class IncidentNoteRead(BaseModel):
    id: int
    incident_id: int
    author_user_id: int
    body: str
    created_at: datetime
