from datetime import date
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import AdminBookingActionResponse, AdminBookingRead
from app.modules.bookings.service import (
    get_admin_booking,
    list_admin_bookings,
    mark_admin_booking_completed,
    mark_admin_booking_no_show,
)
from app.modules.master_shifts.schemas import AdminScheduleResponse
from app.modules.master_shifts.service import get_admin_schedule
from app.modules.reports.schemas import AdminReportSummary
from app.modules.reports.service import get_admin_report_summary
from app.modules.telegram_accounts.schemas import (
    BotTelegramAccountResolve,
    BotTelegramBarbersByMaster,
)
from app.modules.telegram_accounts.service import (
    list_active_barber_telegram_ids_by_master,
    resolve_telegram_account,
)

router = APIRouter()


@router.get("/resolve", response_model=BotTelegramAccountResolve)
def resolve_telegram_account_route(
    telegram_id: int,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    return resolve_telegram_account(db, telegram_id)


@router.get("/barbers/by-master/{master_id}", response_model=BotTelegramBarbersByMaster)
def get_barbers_by_master_route(
    master_id: int,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    return BotTelegramBarbersByMaster(
        master_id=master_id,
        telegram_ids=list_active_barber_telegram_ids_by_master(db, master_id),
    )


@router.get("/bookings", response_model=list[AdminBookingRead])
def get_bot_bookings_route(
    telegram_id: int | None = None,
    date: date | None = None,
    status: str | None = "confirmed",
    master_id: int | None = None,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)

    if telegram_id is None:
        return list_admin_bookings(
            db=db,
            date=date,
            status=status,
            master_id=master_id,
        )

    account = _require_authorized_bot_account(db, telegram_id)
    scoped_master_id = master_id if account.scope == "all" else account.master_id
    return list_admin_bookings(
        db=db,
        date=date,
        status=status,
        master_id=scoped_master_id,
    )


@router.get("/bookings/{booking_id}", response_model=AdminBookingRead)
def get_bot_booking_route(
    booking_id: int,
    telegram_id: int,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    _require_manager_bot_account(db, telegram_id)
    return get_admin_booking(db, booking_id)


@router.get("/schedule", response_model=AdminScheduleResponse)
def get_bot_schedule_route(
    telegram_id: int,
    from_date: date,
    to_date: date,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    _require_authorized_bot_account(db, telegram_id)
    return get_admin_schedule(db, from_date, to_date)


@router.get("/reports/summary", response_model=AdminReportSummary)
def get_bot_report_summary_route(
    telegram_id: int,
    from_date: date,
    to_date: date,
    master_id: int | None = None,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    _require_manager_bot_account(db, telegram_id)
    return get_admin_report_summary(
        db=db,
        from_date=from_date,
        to_date=to_date,
        master_id=master_id,
    )


@router.post("/bookings/{booking_id}/complete", response_model=AdminBookingActionResponse)
def complete_bot_booking_route(
    booking_id: int,
    telegram_id: int,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    _require_manager_bot_account(db, telegram_id)
    return mark_admin_booking_completed(db, booking_id)


@router.post("/bookings/{booking_id}/no-show", response_model=AdminBookingActionResponse)
def no_show_bot_booking_route(
    booking_id: int,
    telegram_id: int,
    x_telegram_bot_token: str | None = Header(default=None, alias="X-Telegram-Bot-Token"),
    db: Session = Depends(get_db),
):
    _require_bot_token(x_telegram_bot_token)
    _require_manager_bot_account(db, telegram_id)
    return mark_admin_booking_no_show(db, booking_id)


def _require_authorized_bot_account(
    db: Session,
    telegram_id: int,
) -> BotTelegramAccountResolve:
    account = resolve_telegram_account(db, telegram_id)
    if not account.authorized:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Telegram account is not authorized",
        )
    return account


def _require_manager_bot_account(
    db: Session,
    telegram_id: int,
) -> BotTelegramAccountResolve:
    account = _require_authorized_bot_account(db, telegram_id)
    if account.role != "manager" or account.scope != "all":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Manager Telegram account is required",
        )
    return account


def _require_bot_token(token: str | None) -> None:
    configured_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not configured_token or not token:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Telegram bot token is required",
        )
    if not hmac.compare_digest(token, configured_token):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Telegram bot token is invalid",
        )
