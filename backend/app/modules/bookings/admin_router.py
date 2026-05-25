from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import BookingAdmin
from app.modules.bookings.service import list_bookings

router = APIRouter()


@router.get("/", response_model=list[BookingAdmin])
def get_admin_bookings(
    status: str | None = None,
    source: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    return list_bookings(
        db=db,
        status=status,
        source=source,
        start_date=start_date,
        end_date=end_date,
    )
