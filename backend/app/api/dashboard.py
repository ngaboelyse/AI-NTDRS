from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.alert import Alert
from app.models.device import Device
from app.models.network_flow import NetworkFlow
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard")


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> DashboardSummary:
    total_devices = db.scalar(select(func.count(Device.id))) or 0
    active_devices = db.scalar(select(func.count(Device.id)).where(Device.status == "online")) or 0
    critical_alerts = db.scalar(select(func.count(Alert.id)).where(Alert.severity == "CRITICAL")) or 0
    flows_analyzed = db.scalar(select(func.count(NetworkFlow.id))) or 0
    threats_today = db.scalar(
        select(func.count(Alert.id)).where(func.date(Alert.created_at) == date.today())
    ) or 0

    if critical_alerts > 0:
        risk_level = "CRITICAL"
    elif threats_today > 10:
        risk_level = "HIGH"
    elif threats_today > 0:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return DashboardSummary(
        total_monitored_devices=total_devices,
        active_devices=active_devices,
        threats_detected_today=threats_today,
        critical_alerts=critical_alerts,
        network_flows_analyzed=flows_analyzed,
        current_risk_level=risk_level,
    )
