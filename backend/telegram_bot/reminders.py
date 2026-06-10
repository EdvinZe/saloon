import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from telegram_bot.api_client import (
    BackendAPIError,
    get_admin_bookings,
    get_barber_telegram_ids_by_master,
)
from telegram_bot.config import load_config
from telegram_bot.formatters import format_barber_appointment_reminder

logger = logging.getLogger(__name__)

sent_reminders: set[str] = set()


async def reminder_loop(bot: Bot) -> None:
    logger.info("[BOT] Barber reminder loop started")

    while True:
        config = load_config()
        try:
            await check_and_send_barber_reminders(bot)
        except Exception as exc:
            logger.warning("[BOT] Barber reminder check failed: %s", exc.__class__.__name__)

        await asyncio.sleep(config.barber_reminder_check_interval_seconds)


async def check_and_send_barber_reminders(bot: Bot) -> None:
    config = load_config()
    timezone = _get_timezone(config.bot_timezone)
    now = datetime.now(timezone)

    try:
        bookings = await get_admin_bookings(
            date=now.date().isoformat(),
            status="confirmed",
        )
    except BackendAPIError as exc:
        logger.warning("[BOT] Barber reminder check failed: %s", exc)
        return

    for booking in bookings:
        if not isinstance(booking, dict):
            continue

        booking_id = booking.get("id")
        if booking_id is None:
            logger.warning(
                "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
                booking_id,
                "missing_booking_id",
            )
            continue

        if booking.get("status") != "confirmed":
            logger.debug(
                "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
                booking_id,
                "not_confirmed",
            )
            continue

        reminder_key = build_reminder_key(booking_id)
        if reminder_key in sent_reminders:
            logger.debug(
                "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
                booking_id,
                "already_sent",
            )
            continue

        if not should_send_reminder(booking, now):
            continue

        master_id = _as_int(booking.get("master_id"))
        if master_id is None:
            logger.warning(
                "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
                booking_id,
                "missing_master_id",
            )
            continue

        try:
            chat_ids = await get_barber_chat_ids_for_master(master_id)
        except BackendAPIError as exc:
            logger.warning(
                "[BOT] Barber reminder routing failed: master_id=%s error=%s",
                master_id,
                exc,
            )
            continue
        if not chat_ids:
            logger.debug(
                "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
                booking_id,
                "no_active_barber_accounts",
            )
            continue

        message = format_barber_appointment_reminder(booking)
        sent_count = 0
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=message)
            except TelegramAPIError as exc:
                logger.warning(
                    "[BOT] Barber reminder check failed: %s",
                    exc.__class__.__name__,
                )
                continue
            except Exception as exc:
                logger.warning(
                    "[BOT] Barber reminder check failed: %s",
                    exc.__class__.__name__,
                )
                continue

            sent_count += 1
            logger.info(
                "[BOT] Barber reminder sent: booking_id=%s master_id=%s chat_id=%s",
                booking_id,
                master_id,
                chat_id,
            )

        if sent_count == len(chat_ids):
            # TODO: Later use NotificationLog table or backend persistent notification log.
            sent_reminders.add(reminder_key)


async def get_barber_chat_ids_for_master(master_id: int) -> list[int]:
    return await get_barber_telegram_ids_by_master(master_id)


def should_send_reminder(booking: dict, now: datetime) -> bool:
    config = load_config()
    start_at = _parse_booking_datetime(booking.get("start_at"), now.tzinfo)
    if start_at is None:
        logger.warning(
            "[BOT] Barber reminder skipped: booking_id=%s reason=%s",
            booking.get("id"),
            "invalid_start_at",
        )
        return False

    if start_at.date() != now.date():
        return False
    if start_at <= now:
        return False

    target = start_at - timedelta(minutes=config.barber_reminder_minutes)
    window_end = now + timedelta(
        seconds=config.barber_reminder_check_interval_seconds + 5
    )
    return now <= target < window_end


def build_reminder_key(booking_id: int | str | None) -> str:
    return f"{booking_id}:reminder_15min"


def _parse_booking_datetime(value: Any, timezone: Any) -> datetime | None:
    if not isinstance(value, str):
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def _get_timezone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        logger.warning("[BOT] Invalid BOT_TIMEZONE value, using default: Europe/Vilnius")
        return ZoneInfo("Europe/Vilnius")


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
