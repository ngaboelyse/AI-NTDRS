from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    resource: str
    result: str
    event_metadata: dict | None = None
    ip_address: str | None = None
    created_at: datetime
    updated_at: datetime
