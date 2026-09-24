from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.model_inference import get_inference_service

router = APIRouter(prefix="/health")


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-ntdrs-backend",
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    return {
        "status": "ready",
        "service": "ai-ntdrs-backend",
        "database": "connected",
        "flow_model_loaded": get_inference_service().is_ready(),
    }
