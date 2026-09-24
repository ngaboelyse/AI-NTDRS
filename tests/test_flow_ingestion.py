from datetime import datetime, timezone

from app.schemas.flow import FlowCreate
from app.services.flow_ingestion import ingest_flow_record


def test_flow_ingestion_creates_detection_and_alert(db_session, seed_device):
    result = ingest_flow_record(
        db_session,
        FlowCreate(
            device_id=seed_device.id,
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

    assert result.risk_score >= 50
    assert result.alert_id is not None
    assert result.severity in {'HIGH', 'CRITICAL'}
