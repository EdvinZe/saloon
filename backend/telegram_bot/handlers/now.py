import logging
from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.api_client import BackendAPIError, get_admin_bookings, get_admin_schedule
from telegram_bot.formatters import format_now_message
from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import back_to_menu_keyboard
from telegram_bot.now_service import build_now_context

router = Router()
logger = logging.getLogger(__name__)


async def _answer_target(
    target: Message | CallbackQuery,
    text: str,
) -> None:
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.answer(text, reply_markup=back_to_menu_keyboard())
        else:
            await target.answer(text[:200], show_alert=True)
        return

    await target.answer(text)


async def _send_now(target: Message | CallbackQuery) -> None:
    ctx = await get_authorized_context(target)
    if ctx is None:
        return

    master_id = ctx.master_id if ctx.scope == "own_master" else None
    today = date.today().isoformat()
    now = datetime.now()

    try:
        schedule = await get_admin_schedule(from_date=today, to_date=today)
        bookings = await get_admin_bookings(
            date=today,
            status="confirmed",
            master_id=master_id,
        )
    except BackendAPIError as exc:
        logger.warning("Could not load current salon status: %s", exc)
        detail = str(exc)
        if detail == "Backend is unavailable. Please try again later.":
            await _answer_target(target, detail)
        else:
            await _answer_target(target, "Could not load current salon status. Please try again.")
        if isinstance(target, CallbackQuery):
            await target.answer()
        return
    except Exception:
        logger.exception("Unexpected error while loading current salon status")
        await _answer_target(target, "Backend is unavailable. Please try again later.")
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    context = build_now_context(
        schedule,
        bookings,
        now,
        role=ctx.role,
        master_id=master_id,
    )
    await _answer_target(
        target,
        format_now_message(context),
    )

    if isinstance(target, CallbackQuery):
        await target.answer()


@router.message(Command("now"))
async def now_command(message: Message) -> None:
    await _send_now(message)


@router.callback_query(F.data == "now")
async def now_callback(callback: CallbackQuery) -> None:
    await _send_now(callback)
