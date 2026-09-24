from datetime import datetime

from pydantic import BaseModel, Field


class FlowCreate(BaseModel):
    device_id: int
    source_ip: str = Field(..., max_length=45)
    destination_ip: str = Field(..., max_length=45)
    source_port: int = Field(..., ge=0, le=65535)
    destination_port: int = Field(..., ge=0, le=65535)
    protocol: str = Field(..., max_length=20)
    packet_count: int = Field(..., ge=0)
    byte_count: int = Field(..., ge=0)
    flow_duration: float = Field(..., ge=0)
    connection_count: int = Field(..., ge=0)
    request_frequency: float = Field(..., ge=0)
    failed_connection_count: int = Field(..., ge=0)
    direction: str = Field(..., max_length=20)
    observed_at: datetime
    payload_collected: bool = False


class FlowIngestionResult(BaseModel):
    flow_id: int
    prediction_id: int
    detection_id: int
    alert_id: int | None = None
    risk_score: float
    severity: str
    threat_category: str
    risk_factors: dict[str, float]
