import logging
from datetime import date, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.api_client import BackendAPIError, get_admin_bookings
from telegram_bot.formatters import format_booking_message, format_bookings_header
from telegram_bot.keyboards import booking_actions_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def _send_bookings(message: Message, label: str, target_date: date) -> None:
    date_text = target_date.isoformat()

    try:
        bookings = await get_admin_bookings(date=date_text, status="confirmed")
    except BackendAPIError as exc:
        logger.warning("Could not load %s bookings: %s", label.lower(), exc)
        await message.answer(str(exc) or "Backend is unavailable. Please try again later.")
        return
    except Exception:
        logger.exception("Unexpected error while loading %s bookings", label.lower())
        await message.answer("Backend is unavailable. Please try again later.")
        return

    if not bookings:
        await message.answer(f"No confirmed bookings for {label.lower()}.")
        return

    await message.answer(format_bookings_header(label, date_text))

    for booking in bookings:
        booking_id = booking.get("id")
        reply_markup = booking_actions_keyboard(booking_id) if isinstance(booking_id, int) else None
        await message.answer(format_booking_message(booking), reply_markup=reply_markup)


@router.message(Command("today"))
async def today_command(message: Message) -> None:
    await _send_bookings(message, "Today", date.today())


@router.message(Command("tomorrow"))
async def tomorrow_command(message: Message) -> None:
    await _send_bookings(message, "Tomorrow", date.today() + timedelta(days=1))
