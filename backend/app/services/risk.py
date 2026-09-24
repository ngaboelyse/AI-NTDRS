from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.network_flow import NetworkFlow


@dataclass
class RiskWeights:
    """Configurable risk scoring weights."""
    failed_connections_weight: float = 6.0
    request_frequency_weight: float = 4.0
    connection_count_weight: float = 2.0
    packet_count_weight: float = 0.001
    byte_count_weight: float = 0.00001
    flow_duration_weight: float = 1.5
    anomaly_score_weight: float = 15.0


@dataclass
class RiskResult:
    score: float
    severity: str
    factors: dict[str, float]
    anomaly_detected: bool = False
    confidence: float | None = None


def _severity_from_score(score: float) -> str:
    if score >= 75:
        return 'CRITICAL'
    if score >= 50:
        return 'HIGH'
    if score >= 25:
        return 'MODERATE'
    return 'LOW'


def calculate_flow_risk(
    flow: NetworkFlow,
    weights: Optional[RiskWeights] = None,
    anomaly_score: Optional[float] = None,
) -> RiskResult:
    """
    Calculate risk score for a network flow.
    
    Args:
        flow: The network flow to score
        weights: Custom risk weights (uses defaults if None)
        anomaly_score: Optional ML anomaly score (0-1 scale)
    
    Returns:
        RiskResult with comprehensive scoring breakdown
    """
    if weights is None:
        weights = RiskWeights()
    
    # Component calculations with adaptive capping
    failed_connections = min(flow.failed_connection_count * weights.failed_connections_weight, 40.0)
    frequency_component = min(flow.request_frequency * weights.request_frequency_weight, 25.0)
    connection_component = min(flow.connection_count * weights.connection_count_weight, 15.0)
    traffic_component = min(
        (flow.packet_count * weights.packet_count_weight) + (flow.byte_count * weights.byte_count_weight),
        10.0,
    )
    duration_component = min(flow.flow_duration * weights.flow_duration_weight, 10.0)

    # Add ML anomaly score if provided
    anomaly_component = 0.0
    anomaly_detected = False
    
    if anomaly_score is not None and anomaly_score > 0.5:
        anomaly_component = min(anomaly_score * weights.anomaly_score_weight, 20.0)
        anomaly_detected = True

    score = min(
        failed_connections 
        + frequency_component 
        + connection_component 
        + traffic_component 
        + duration_component
        + anomaly_component,
        100.0,
    )

    return RiskResult(
        score=round(score, 2),
        severity=_severity_from_score(score),
        factors={
            'failed_connections': round(failed_connections, 2),
            'request_frequency': round(frequency_component, 2),
            'connection_count': round(connection_component, 2),
            'traffic_volume': round(traffic_component, 2),
            'duration': round(duration_component, 2),
            'anomaly_score': round(anomaly_component, 2),
        },
        anomaly_detected=anomaly_detected,
        confidence=None,
    )
