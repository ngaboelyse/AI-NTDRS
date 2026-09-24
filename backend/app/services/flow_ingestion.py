from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.detection import Detection
from app.models.device import Device
from app.models.model_prediction import ModelPrediction
from app.models.network_flow import NetworkFlow
from app.models.risk_score import RiskScore
from app.schemas.flow import FlowCreate, FlowIngestionResult
from app.services.model_registry import ensure_demo_model_version, ensure_trained_demo_model_version
from app.services.risk import calculate_flow_risk, RiskWeights
from app.services.model_inference import get_inference_service


def ingest_flow_record(db: Session, payload: FlowCreate) -> FlowIngestionResult:
    device = db.get(Device, payload.device_id)
    if device is None:
        raise ValueError('Device not found')

    flow = NetworkFlow(
        device_id=payload.device_id,
        source_ip=payload.source_ip,
        destination_ip=payload.destination_ip,
        source_port=payload.source_port,
        destination_port=payload.destination_port,
        protocol=payload.protocol,
        packet_count=payload.packet_count,
        byte_count=payload.byte_count,
        flow_duration=payload.flow_duration,
        connection_count=payload.connection_count,
        request_frequency=payload.request_frequency,
        failed_connection_count=payload.failed_connection_count,
        direction=payload.direction,
        observed_at=payload.observed_at,
        payload_collected=payload.payload_collected,
    )
    db.add(flow)
    db.flush()

    # Attempt ML-based anomaly detection
    inference_service = get_inference_service()
    ml_inference = None
    anomaly_score = 0.0
    
    if inference_service.is_ready():
        try:
            # Prepare features for ML model
            flow_data = pd.DataFrame([{
                'packet_count': flow.packet_count,
                'byte_count': flow.byte_count,
                'flow_duration': flow.flow_duration,
                'connection_count': flow.connection_count,
                'request_frequency': flow.request_frequency,
                'failed_connection_count': flow.failed_connection_count,
                'source_port': flow.source_port,
                'destination_port': flow.destination_port,
                'protocol': flow.protocol,
                'direction': flow.direction,
                'device_id': str(flow.device_id),
                'source_ip': flow.source_ip,
                'destination_ip': flow.destination_ip,
            }])
            
            ml_inference = inference_service.infer(flow_data)
            anomaly_score = ml_inference.anomaly_score
            
        except Exception as e:
            # Fallback to heuristic if ML fails
            import logging
            logging.warning(f"ML inference failed, using heuristic: {e}")
    
    # Calculate risk with ML anomaly score if available
    risk = calculate_flow_risk(
        flow,
        weights=RiskWeights(),
        anomaly_score=anomaly_score if anomaly_score > 0 else None
    )
    
    # Get model version (use ML model if available, otherwise fallback)
    model_version = ensure_trained_demo_model_version(db) if ml_inference else ensure_demo_model_version(db)

    prediction = ModelPrediction(
        model_version_id=model_version.id,
        flow_id=flow.id,
        predicted_label=ml_inference.predicted_label if ml_inference else ('Suspicious' if risk.score >= 50 else 'Normal'),
        anomaly_score=ml_inference.anomaly_score if ml_inference else (risk.score / 100.0),
        confidence=ml_inference.confidence if ml_inference else (0.94 if risk.score >= 50 else 0.78),
        explanation_summary=ml_inference.explanation if ml_inference else 'Heuristic risk calculation based on flow metadata.',
        predicted_at=datetime.now(timezone.utc),
    )
    db.add(prediction)
    db.flush()

    detection = Detection(
        device_id=device.id,
        flow_id=flow.id,
        prediction_id=prediction.id,
        threat_category=(
            ml_inference.predicted_label
            if ml_inference and ml_inference.predicted_label != 'Unknown'
            else ('Suspicious flow anomaly' if risk.score >= 50 else 'Normal')
        ),
        severity=risk.severity,
        risk_score=risk.score,
        reason=prediction.explanation_summary,
        detected_at=datetime.now(timezone.utc),
    )
    db.add(detection)
    db.flush()

    alert = None
    if risk.score >= 50:
        alert = Alert(
            alert_id=f'ALT-{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}-{flow.id}',
            detection_id=detection.id,
            device_id=device.id,
            source_ip=flow.source_ip,
            destination_ip=flow.destination_ip,
            protocol=flow.protocol,
            threat_category=detection.threat_category,
            risk_score=risk.score,
            severity=risk.severity,
            detection_reason=detection.reason,
            model_confidence=prediction.confidence,
            status='NEW',
            recommended_action='Investigate device activity and verify authorization.',
        )
        db.add(alert)
        device.alert_count += 1
        device.risk_score = max(device.risk_score, risk.score)
        device.activity_level = 'high' if risk.score >= 75 else 'elevated'
        db.flush()

    risk_score = RiskScore(
        device_id=device.id,
        alert_id=alert.id if alert is not None else None,
        incident_id=None,
        score=risk.score,
        severity=risk.severity,
        contributing_factors=risk.factors,
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(risk_score)
    db.commit()

    return FlowIngestionResult(
        flow_id=flow.id,
        prediction_id=prediction.id,
        detection_id=detection.id,
        alert_id=alert.id if alert is not None else None,
        risk_score=risk.score,
        severity=risk.severity,
        threat_category=detection.threat_category,
        risk_factors=risk.factors,
    )
