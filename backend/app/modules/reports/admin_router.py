from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.reports.schemas import AdminReportSummary
from app.modules.reports.service import get_admin_report_summary

router = APIRouter()


@router.get("/summary", response_model=AdminReportSummary)
def get_admin_report_summary_route(
    from_date: date,
    to_date: date,
    master_id: int | None = None,
    db: Session = Depends(get_db),
):
    return get_admin_report_summary(
        db=db,
        from_date=from_date,
        to_date=to_date,
        master_id=master_id,
    )
