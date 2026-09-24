from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ResponseActionRequestCreate(BaseModel):
    action_type: Literal["ISOLATE_ENDPOINT", "BLOCK_INDICATOR", "DISABLE_ACCOUNT"]
    details: str = Field(..., min_length=10, max_length=2000)
    incident_id: int | None = None
    alert_id: int | None = None

    @model_validator(mode="after")
    def require_target(self):
        if self.incident_id is None and self.alert_id is None:
            raise ValueError("An incident_id or alert_id is required")
        return self


class ResponseActionRequestRead(BaseModel):
    id: int
    incident_id: int | None
    alert_id: int | None
    action_type: str
    details: str
    status: str
    requested_by_user_id: int
    approved_by_user_id: int | None
    rejected_by_user_id: int | None = None
    requested_at: datetime
    approved_at: datetime | None


class ResponseActionRead(BaseModel):
    id: int
    incident_id: int | None
    alert_id: int | None
    action_type: str
    is_simulated: bool
    requested_by_user_id: int
    approved_by_user_id: int | None
    details: str | None
    executed_at: datetime
    result: str
