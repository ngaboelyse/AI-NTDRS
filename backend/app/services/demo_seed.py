from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.network_flow import NetworkFlow
from app.schemas.flow import FlowCreate
from app.services.flow_ingestion import ingest_flow_record


def seed_demo_data(db: Session) -> None:
    device_count = db.scalar(select(func.count(Device.id))) or 0
    if device_count == 0:
        primary_device = Device(
            device_identifier='PC-025',
            ip_address='192.168.1.25',
            hostname='pc-025.university.local',
            device_type='Workstation',
            last_seen=datetime.now(timezone.utc),
            activity_level='normal',
            risk_score=0.0,
            alert_count=0,
            status='online',
        )
        secondary_device = Device(
            device_identifier='PC-041',
            ip_address='192.168.1.41',
            hostname='pc-041.university.local',
            device_type='Workstation',
            last_seen=datetime.now(timezone.utc),
            activity_level='normal',
            risk_score=0.0,
            alert_count=0,
            status='online',
        )
        db.add_all([primary_device, secondary_device])
        db.commit()

    devices = db.scalars(select(Device).order_by(Device.id)).all()
    if not devices:
        return

    primary_device = devices[0]
    secondary_device = devices[1] if len(devices) > 1 else devices[0]

    flow_count = db.scalar(select(func.count(NetworkFlow.id))) or 0
    if flow_count == 0:
        ingest_flow_record(
            db,
            FlowCreate(
                device_id=secondary_device.id,
                source_ip='192.168.1.41',
                destination_ip='192.168.1.10',
                source_port=49512,
                destination_port=80,
                protocol='TCP',
                packet_count=48,
                byte_count=32140,
                flow_duration=12.4,
                connection_count=3,
                request_frequency=1.2,
                failed_connection_count=0,
                direction='outbound',
                observed_at=datetime.now(timezone.utc),
                payload_collected=False,
            ),
        )

        ingest_flow_record(
            db,
            FlowCreate(
                device_id=primary_device.id,
                source_ip='192.168.1.25',
                destination_ip='192.168.1.200',
                source_port=51432,
                destination_port=22,
                protocol='TCP',
                packet_count=980,
                byte_count=764000,
                flow_duration=7.2,
                connection_count=26,
                request_frequency=8.7,
                failed_connection_count=14,
                direction='outbound',
                observed_at=datetime.now(timezone.utc),
                payload_collected=False,
            ),
        )
