import logging
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.bookings.models import Booking
from app.modules.masters.models import Master
from app.modules.reports.schemas import (
    AdminReportDailySummary,
    AdminReportMasterSummary,
    AdminReportServiceSummary,
    AdminReportSummary,
)

logger = logging.getLogger(__name__)

MAX_REPORT_RANGE_DAYS = 366
DEFAULT_CURRENCY = "EUR"


def get_admin_report_summary(
    db: Session,
    from_date: date,
    to_date: date,
    master_id: int | None = None,
) -> AdminReportSummary:
    _validate_report_range(from_date, to_date)

    if master_id is not None and db.get(Master, master_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master not found: {master_id}",
        )

    logger.info(
        "[ADMIN] Report summary requested: from_date=%s to_date=%s master_id=%s",
        from_date,
        to_date,
        master_id,
    )

    bookings = _list_report_bookings(
        db=db,
        from_date=from_date,
        to_date=to_date,
        master_id=master_id,
    )

    totals = _empty_summary_counts()
    master_totals: dict[int, dict[str, object]] = {}
    service_totals: dict[int, dict[str, object]] = {}
    daily_totals = _empty_daily_totals(from_date, to_date)
    currencies: defaultdict[str, int] = defaultdict(int)

    for booking in bookings:
        booking_date = booking.start_at.date()
        currencies[booking.currency or DEFAULT_CURRENCY] += 1

        _apply_booking_to_counts(totals, booking)

        master_summary = master_totals.setdefault(
            booking.master_id,
            _empty_master_counts(
                master_id=booking.master_id,
                master_name=_format_master_name(booking.master),
            ),
        )
        _apply_booking_to_counts(master_summary, booking)

        service_summary = service_totals.setdefault(
            booking.service_id,
            _empty_service_counts(
                service_id=booking.service_id,
                service_name=booking.service.name if booking.service else "",
            ),
        )
        _apply_booking_to_counts(service_summary, booking)

        _apply_booking_to_counts(daily_totals[booking_date], booking)

    return AdminReportSummary(
        from_date=from_date,
        to_date=to_date,
        master_id=master_id,
        currency=_most_common_currency(currencies),
        by_master=[
            AdminReportMasterSummary(**summary)
            for summary in sorted(
                master_totals.values(),
                key=lambda item: (str(item["master_name"]), int(item["master_id"])),
            )
        ],
        by_service=[
            AdminReportServiceSummary(**summary)
            for summary in sorted(
                service_totals.values(),
                key=lambda item: (str(item["service_name"]), int(item["service_id"])),
            )
        ],
        daily_breakdown=[
            AdminReportDailySummary(**daily_totals[current_date])
            for current_date in sorted(daily_totals)
        ],
        **totals,
    )


def _validate_report_range(from_date: date, to_date: date) -> None:
    if from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report date range",
        )

    if to_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Future reports are not available",
        )

    if (to_date - from_date).days + 1 > MAX_REPORT_RANGE_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report date range cannot exceed {MAX_REPORT_RANGE_DAYS} days",
        )


def _list_report_bookings(
    db: Session,
    from_date: date,
    to_date: date,
    master_id: int | None,
) -> list[Booking]:
    statement = (
        select(Booking)
        .options(
            selectinload(Booking.master),
            selectinload(Booking.service),
        )
        .where(
            Booking.start_at >= datetime.combine(from_date, time.min),
            Booking.start_at <= datetime.combine(to_date, time.max),
        )
        .order_by(Booking.start_at.asc(), Booking.id.asc())
    )

    if master_id is not None:
        statement = statement.where(Booking.master_id == master_id)

    return list(db.scalars(statement).all())


def _empty_summary_counts() -> dict[str, int]:
    return {
        "total_bookings": 0,
        "confirmed_count": 0,
        "completed_count": 0,
        "cancelled_count": 0,
        "no_show_count": 0,
        "paid_deposits_cents": 0,
        "refunded_deposits_cents": 0,
        "net_deposits_cents": 0,
    }


def _empty_master_counts(master_id: int, master_name: str) -> dict[str, object]:
    return {
        "master_id": master_id,
        "master_name": master_name,
        **_empty_summary_counts(),
    }


def _empty_service_counts(service_id: int, service_name: str) -> dict[str, object]:
    counts = _empty_summary_counts()
    counts.pop("confirmed_count")
    return {
        "service_id": service_id,
        "service_name": service_name,
        **counts,
    }


def _empty_daily_counts(current_date: date) -> dict[str, object]:
    counts = _empty_summary_counts()
    counts.pop("confirmed_count")
    return {
        "date": current_date,
        **counts,
    }


def _empty_daily_totals(
    from_date: date,
    to_date: date,
) -> dict[date, dict[str, object]]:
    total_days = (to_date - from_date).days + 1
    return {
        from_date + timedelta(days=day_offset): _empty_daily_counts(
            from_date + timedelta(days=day_offset)
        )
        for day_offset in range(total_days)
    }


def _apply_booking_to_counts(counts: dict[str, object], booking: Booking) -> None:
    counts["total_bookings"] = int(counts["total_bookings"]) + 1

    status_count_key = f"{booking.status}_count"
    if status_count_key in counts:
        counts[status_count_key] = int(counts[status_count_key]) + 1

    if booking.deposit_status == "paid":
        counts["paid_deposits_cents"] = (
            int(counts["paid_deposits_cents"]) + booking.deposit_amount_cents
        )
    elif booking.deposit_status == "refunded":
        counts["refunded_deposits_cents"] = (
            int(counts["refunded_deposits_cents"]) + booking.deposit_amount_cents
        )

    counts["net_deposits_cents"] = (
        int(counts["paid_deposits_cents"]) - int(counts["refunded_deposits_cents"])
    )


def _format_master_name(master: Master | None) -> str:
    if master is None:
        return ""

    return f"{master.first_name} {master.last_name}".strip()


def _most_common_currency(currencies: defaultdict[str, int]) -> str:
    if not currencies:
        return DEFAULT_CURRENCY

    return max(currencies.items(), key=lambda item: item[1])[0]
