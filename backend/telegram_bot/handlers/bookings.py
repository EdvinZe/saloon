import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.api_client import BackendAPIError, get_admin_bookings
from telegram_bot.formatters import format_booking_message, format_bookings_header
from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import back_to_menu_keyboard, booking_actions_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def _answer_target(target: Message | CallbackQuery, text: str, **kwargs) -> None:
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.answer(text, **kwargs)
        else:
            await target.answer(text[:200], show_alert=True)
        return

    await target.answer(text, **kwargs)


def _callback_menu_markup(target: Message | CallbackQuery):
    return back_to_menu_keyboard() if isinstance(target, CallbackQuery) else None


async def _send_bookings(target: Message | CallbackQuery, label: str, target_date: date) -> None:
    ctx = await get_authorized_context(target)
    if ctx is None:
        return

    date_text = target_date.isoformat()
    master_id = ctx.master_id if ctx.scope == "own_master" else None

    try:
        bookings = await get_admin_bookings(
            date=date_text,
            status="confirmed",
            master_id=master_id,
            telegram_id=ctx.telegram_user_id,
        )
    except BackendAPIError as exc:
        logger.warning("Could not load %s bookings: %s", label.lower(), exc)
        detail = str(exc)
        if detail == "Backend is unavailable. Please try again later.":
            await _answer_target(target, detail, reply_markup=_callback_menu_markup(target))
        else:
            await _answer_target(
                target,
                "Could not load bookings. Please try again.",
                reply_markup=_callback_menu_markup(target),
            )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return
    except Exception:
        logger.exception("Unexpected error while loading %s bookings", label.lower())
        await _answer_target(
            target,
            "Backend is unavailable. Please try again later.",
            reply_markup=_callback_menu_markup(target),
        )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    if not bookings:
        await _answer_target(
            target,
            f"No confirmed bookings for {label.lower()}.",
            reply_markup=_callback_menu_markup(target),
        )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    scope_label = "All confirmed bookings" if ctx.scope == "all" else "Your confirmed bookings"
    await _answer_target(
        target,
        format_bookings_header(f"{scope_label} for {label.lower()}", date_text),
    )

    for booking in bookings:
        booking_id = booking.get("id")
        reply_markup = (
            booking_actions_keyboard(booking_id)
            if ctx.role == "manager" and isinstance(booking_id, int)
            else None
        )
        await _answer_target(target, format_booking_message(booking), reply_markup=reply_markup)

    if isinstance(target, CallbackQuery):
        await _answer_target(target, "Use the menu to continue.", reply_markup=back_to_menu_keyboard())

    if isinstance(target, CallbackQuery):
        await target.answer()


@router.message(Command("today"))
async def today_command(message: Message) -> None:
    await _send_bookings(message, "Today", date.today())


@router.message(Command("tomorrow"))
async def tomorrow_command(message: Message) -> None:
    await _send_bookings(message, "Tomorrow", date.today() + timedelta(days=1))


@router.callback_query(F.data == "manager_bookings:today")
async def today_bookings_callback(callback: CallbackQuery) -> None:
    await _send_bookings(callback, "Today", date.today())


@router.callback_query(F.data == "manager_bookings:tomorrow")
async def tomorrow_bookings_callback(callback: CallbackQuery) -> None:
    await _send_bookings(callback, "Tomorrow", date.today() + timedelta(days=1))


@router.callback_query(F.data == "barber_bookings:today")
async def barber_today_bookings_callback(callback: CallbackQuery) -> None:
    await _send_bookings(callback, "Today", date.today())


@router.callback_query(F.data == "barber_bookings:tomorrow")
async def barber_tomorrow_bookings_callback(callback: CallbackQuery) -> None:
    await _send_bookings(callback, "Tomorrow", date.today() + timedelta(days=1))
