from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.copilot import CopilotQueryRequest, CopilotSummary
from app.services.copilot import respond_to_copilot

router = APIRouter(prefix="/copilot")


@router.post("/query", response_model=CopilotSummary)
def query_copilot(
    payload: CopilotQueryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> CopilotSummary:
    return respond_to_copilot(
        db,
        payload.query,
        [(message.role, message.content) for message in payload.history],
    )
