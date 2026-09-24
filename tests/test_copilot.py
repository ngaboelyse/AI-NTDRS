from datetime import datetime, timezone

from app.models.alert import Alert
from app.models.detection import Detection
from app.models.incident import Incident
from app.models.model_prediction import ModelPrediction
from app.models.model_version import ModelVersion
from app.models.network_flow import NetworkFlow


def test_copilot_summary_returns_grounded_data(client, seed_user, seed_device, db_session):
    model_version = ModelVersion(
        model_name='Demo',
        version='v-test-copilot',
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
        source_port=49152,
        destination_port=443,
        protocol='TCP',
        packet_count=320,
        byte_count=210000,
        flow_duration=6.8,
        connection_count=12,
        request_frequency=5.3,
        failed_connection_count=3,
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
        anomaly_score=0.82,
        confidence=0.91,
        explanation_summary='Frequent connections',
        predicted_at=datetime.now(timezone.utc),
    )
    db_session.add(prediction)
    db_session.flush()

    detection = Detection(
        device_id=seed_device.id,
        flow_id=flow.id,
        prediction_id=prediction.id,
        threat_category='Suspicious flow anomaly',
        severity='HIGH',
        risk_score=87.0,
        reason='Copilot test detection',
        detected_at=datetime.now(timezone.utc),
    )
    db_session.add(detection)
    db_session.flush()

    alert = Alert(
        alert_id='ALT-COPILOT-001',
        detection_id=detection.id,
        device_id=seed_device.id,
        source_ip='192.168.1.25',
        destination_ip='192.168.1.10',
        protocol='TCP',
        threat_category='Suspicious flow anomaly',
        risk_score=87.0,
        severity='HIGH',
        detection_reason='Copilot test detection',
        model_confidence=0.91,
        status='NEW',
        recommended_action='Investigate device activity',
    )
    incident = Incident(
        incident_code='INC-COPILOT-001',
        title='Suspicious activity on PC-025',
        status='NEW',
        summary='Demo incident for copilot coverage',
        assigned_analyst_id=seed_user.id,
        opened_at=datetime.now(timezone.utc),
        last_activity_at=datetime.now(timezone.utc),
    )
    db_session.add_all([alert, incident])
    db_session.commit()

    response = client.post(
        '/api/copilot/query',
        json={'query': "Summarize today's incidents"},
    )

    assert response.status_code == 200
    body = response.json()
    assert 'devices' in body['answer'].lower()
    assert body['facts']
    assert body['related_devices']
    assert body['related_alerts']
