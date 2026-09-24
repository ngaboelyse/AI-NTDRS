from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.report import Report
from app.schemas.report import ReportRead

router = APIRouter(prefix="/reports")


@router.get("", response_model=list[ReportRead])
def list_reports(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> list[ReportRead]:
    reports = db.scalars(select(Report).order_by(Report.id.desc())).all()
    return [ReportRead.model_validate(report, from_attributes=True) for report in reports]


@router.get("/{report_id}", response_model=ReportRead)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> ReportRead:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportRead.model_validate(report, from_attributes=True)
