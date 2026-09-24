from datetime import datetime, timezone
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.device import Device
from app.models.sensor_event_receipt import SensorEventReceipt
from app.schemas.flow import FlowCreate, FlowIngestionResult
from app.schemas.telemetry import SuricataFlowEvent
from app.services.flow_ingestion import ingest_flow_record

router = APIRouter(prefix="/telemetry")


@router.post("/suricata/flow", response_model=FlowIngestionResult)
def ingest_suricata_flow(
    event: SuricataFlowEvent,
    db: Session = Depends(get_db),
    sensor_key: str = Header(default="", alias="X-Sensor-Key"),
    sensor_id: str = Header(default="suricata", alias="X-Sensor-ID", min_length=1, max_length=60),
    event_id: str = Header(default="", alias="X-Event-ID", min_length=1, max_length=110),
) -> FlowIngestionResult:
    expected_key = settings.sensor_api_key
    if not expected_key:
        raise HTTPException(status_code=503, detail="Sensor ingestion is not configured")
    if not secrets.compare_digest(sensor_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid sensor credentials")

    event_key = f"{sensor_id}:{event_id}"
    existing = db.get(SensorEventReceipt, event_key)
    if existing is not None:
        return FlowIngestionResult.model_validate(existing.result)

    src_ip = str(event.src_ip)
    dest_ip = str(event.dest_ip)
    device = db.scalar(select(Device).where(Device.ip_address == src_ip).order_by(Device.id))
    if device is None:
        device = db.scalar(select(Device).where(Device.ip_address == dest_ip).order_by(Device.id))
    if device is None:
        raise HTTPException(status_code=422, detail="Onboard the source or destination device before ingesting its flow")
    direction = "outbound" if device.ip_address == src_ip else "inbound"

    flow_data = event.flow
    packet_count = int(flow_data.get("pkts_toserver", 0) or 0) + int(flow_data.get("pkts_toclient", 0) or 0)
    byte_count = int(flow_data.get("bytes_toserver", 0) or 0) + int(flow_data.get("bytes_toclient", 0) or 0)
    duration = max(0.0, float(flow_data.get("age", 0) or 0))
    payload = FlowCreate(
        device_id=device.id,
        source_ip=src_ip,
        destination_ip=dest_ip,
        source_port=event.src_port or 0,
        destination_port=event.dest_port or 0,
        protocol=event.proto.upper(),
        packet_count=packet_count,
        byte_count=byte_count,
        flow_duration=duration,
        connection_count=1,
        request_frequency=0,
        failed_connection_count=0,
        direction=direction,
        observed_at=event.timestamp,
        payload_collected=False,
    )
    try:
        result = ingest_flow_record(db, payload, commit=False)
        db.add(SensorEventReceipt(
            event_key=event_key,
            sensor_id=sensor_id,
            result=result.model_dump(mode="json"),
            received_at=datetime.now(timezone.utc),
        ))
        db.add(AuditLog(
            action="telemetry.flow_ingested",
            resource=f"sensor:{sensor_id}",
            result="success",
            event_metadata={"event_id": event_id, "flow_id": result.flow_id},
        ))
        db.commit()
        return result
    except IntegrityError:
        db.rollback()
        existing = db.get(SensorEventReceipt, event_key)
        if existing is not None:
            return FlowIngestionResult.model_validate(existing.result)
        raise HTTPException(status_code=409, detail="Sensor event could not be recorded")
    except Exception:
        db.rollback()
        raise
