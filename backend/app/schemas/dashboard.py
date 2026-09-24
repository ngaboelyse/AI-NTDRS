from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_monitored_devices: int
    active_devices: int
    threats_detected_today: int
    critical_alerts: int
    network_flows_analyzed: int
    current_risk_level: str
