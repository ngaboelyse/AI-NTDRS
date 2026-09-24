from datetime import datetime, timezone

from app.models.alert import Alert
from app.models.detection import Detection
from app.models.model_prediction import ModelPrediction
from app.models.model_version import ModelVersion
from app.models.network_flow import NetworkFlow
from app.models.risk_score import RiskScore


def test_dashboard_summary(client, seed_user, seed_device, db_session):
    model_version = ModelVersion(
        model_name='Demo',
        version='v-test',
        algorithm='RandomForest',
        dataset_name='CICIDS2017',
        training_started_at=datetime.now(timezone.utc),
        training_completed_at=datetime.now(timezone.utc),
    )
    db_session.add(model_version)
    db_session.flush()

    flow = NetworkFlow(
        device_id=seed_device.id,
        source_ip='192.168.1.25',
        destination_ip='192.168.1.10',
        source_port=45000,
        destination_port=22,
        protocol='TCP',
        packet_count=100,
        byte_count=10000,
        flow_duration=4.2,
        connection_count=5,
        request_frequency=2.5,
        failed_connection_count=1,
        direction='outbound',
        observed_at=datetime.now(timezone.utc),
        payload_collected=False,
    )
    db_session.add(flow)
    db_session.flush()

    prediction = ModelPrediction(
        model_version_id=model_version.id,
        flow_id=flow.id,
        predicted_label='Suspicious',
        anomaly_score=0.85,
        confidence=0.92,
        explanation_summary='High connection frequency',
        predicted_at=datetime.now(timezone.utc),
    )
    db_session.add(prediction)
    db_session.flush()

    detection = Detection(
        device_id=seed_device.id,
        flow_id=flow.id,
        prediction_id=prediction.id,
        threat_category='Suspicious flow anomaly',
        severity='CRITICAL',
        risk_score=91.0,
        reason='Test detection',
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(detection)
    db_session.flush()

    alert = Alert(
        alert_id='ALT-TEST-001',
        detection_id=detection.id,
        device_id=seed_device.id,
        source_ip='192.168.1.25',
        destination_ip='192.168.1.10',
        protocol='TCP',
        threat_category='Suspicious flow anomaly',
        risk_score=91.0,
        severity='CRITICAL',
        detection_reason='Test detection',
        model_confidence=0.92,
        status='NEW',
        recommended_action='Investigate device activity',
    )
    db_session.add(alert)
    db_session.add(RiskScore(
        device_id=seed_device.id,
        alert_id=None,
        incident_id=None,
        score=91.0,
        severity='CRITICAL',
        contributing_factors={'failed_connections': 20.0},
        calculated_at=datetime.now(timezone.utc),
    ))
    db_session.commit()

    response = client.get('/api/dashboard/summary')

    assert response.status_code == 200
    body = response.json()
    assert body['total_monitored_devices'] >= 1
    assert body['critical_alerts'] >= 1


def test_device_list(client, seed_user, seed_device):
    response = client.get('/api/devices')

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert body[0]['device_identifier'] == 'PC-025'
