from fastapi import APIRouter

from app.api.copilot import router as copilot_router
from app.api.audit_logs import router as audit_logs_router
from app.api.incidents import router as incidents_router
from app.api.reports import router as reports_router
from app.api.flows import router as flows_router
from app.api.alerts import router as alerts_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.devices import router as devices_router
from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(devices_router, tags=["devices"])
api_router.include_router(alerts_router, tags=["alerts"])
api_router.include_router(flows_router, tags=["flows"])
api_router.include_router(incidents_router, tags=["incidents"])
api_router.include_router(reports_router, tags=["reports"])
api_router.include_router(audit_logs_router, tags=["audit-logs"])
api_router.include_router(copilot_router, tags=["copilot"])
api_router.include_router(health_router, tags=["health"])
