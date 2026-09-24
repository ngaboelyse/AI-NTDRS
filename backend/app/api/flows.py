from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.network_flow import NetworkFlow
from app.schemas.flow import FlowCreate, FlowIngestionResult
from app.services.flow_ingestion import ingest_flow_record

router = APIRouter(prefix="/flows")


@router.get("")
def list_flows(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    device_id: Optional[int] = None,
    protocol: Optional[str] = None,
    source_ip: Optional[str] = None,
    destination_ip: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    query = select(NetworkFlow)
    
    filters = []
    if device_id is not None:
        filters.append(NetworkFlow.device_id == device_id)
    if protocol:
        filters.append(NetworkFlow.protocol.ilike(protocol))
    if source_ip:
        filters.append(NetworkFlow.source_ip == source_ip)
    if destination_ip:
        filters.append(NetworkFlow.destination_ip == destination_ip)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(NetworkFlow.observed_at.desc()).offset(skip).limit(limit)
    flows = db.scalars(query).all()
    
    return [
        {
            "id": flow.id,
            "device_id": flow.device_id,
            "source_ip": flow.source_ip,
            "destination_ip": flow.destination_ip,
            "protocol": flow.protocol,
            "packet_count": flow.packet_count,
            "byte_count": flow.byte_count,
            "flow_duration": flow.flow_duration,
            "failed_connection_count": flow.failed_connection_count,
            "observed_at": flow.observed_at,
        }
        for flow in flows
    ]


@router.post("", response_model=FlowIngestionResult)
def ingest_flow(
    payload: FlowCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin", "Security Analyst")),
) -> FlowIngestionResult:
    try:
        return ingest_flow_record(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
