import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.api_client import BackendAPIError, get_admin_bookings
from telegram_bot.auth import is_manager
from telegram_bot.formatters import format_booking_message, format_bookings_header
from telegram_bot.keyboards import booking_actions_keyboard

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


async def _send_bookings(target: Message | CallbackQuery, label: str, target_date: date) -> None:
    user_id = target.from_user.id if target.from_user else None
    if user_id is None or not is_manager(user_id):
        if isinstance(target, CallbackQuery):
            await target.answer("Access denied.", show_alert=True)
        else:
            await target.answer("Access denied.")
        return

    date_text = target_date.isoformat()

    try:
        bookings = await get_admin_bookings(
            date=date_text,
            status="confirmed",
        )
    except BackendAPIError as exc:
        logger.warning("Could not load %s bookings: %s", label.lower(), exc)
        detail = str(exc)
        if detail == "Backend is unavailable. Please try again later.":
            await _answer_target(target, detail)
        else:
            await _answer_target(target, "Could not load bookings. Please try again.")
        if isinstance(target, CallbackQuery):
            await target.answer()
        return
    except Exception:
        logger.exception("Unexpected error while loading %s bookings", label.lower())
        await _answer_target(target, "Backend is unavailable. Please try again later.")
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    if not bookings:
        await _answer_target(target, f"No confirmed bookings for {label.lower()}.")
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    await _answer_target(
        target,
        format_bookings_header(f"All confirmed bookings for {label.lower()}", date_text),
    )

    for booking in bookings:
        booking_id = booking.get("id")
        reply_markup = booking_actions_keyboard(booking_id) if isinstance(booking_id, int) else None
        await _answer_target(target, format_booking_message(booking), reply_markup=reply_markup)

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
