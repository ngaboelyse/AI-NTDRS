from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class SuricataFlowEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: Literal["flow"]
    timestamp: datetime
    src_ip: IPvAnyAddress
    dest_ip: IPvAnyAddress
    src_port: int | None = Field(default=None, ge=0, le=65535)
    dest_port: int | None = Field(default=None, ge=0, le=65535)
    proto: str = Field(min_length=1, max_length=20)
    flow: dict = Field(default_factory=dict)
