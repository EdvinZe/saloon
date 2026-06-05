import logging
from collections.abc import Callable

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.api_client import BackendAPIError, get_admin_report_summary
from telegram_bot.auth import is_manager
from telegram_bot.formatters import format_report_summary
from telegram_bot.report_presets import (
    get_last_month_range,
    get_last_week_range,
    get_this_month_range,
    get_this_week_range,
    get_today_range,
    get_yesterday_range,
)

router = Router()
logger = logging.getLogger(__name__)

PresetRangeFactory = Callable[[], tuple[str, str]]

REPORT_PRESETS: dict[str, tuple[str, str, PresetRangeFactory]] = {
    "today": ("📊 Today summary", "today summary", get_today_range),
    "yesterday": ("📊 Yesterday summary", "yesterday summary", get_yesterday_range),
    "this_week": ("📆 This week summary", "this week summary", get_this_week_range),
    "last_week": ("📆 Last week summary", "last week summary", get_last_week_range),
    "this_month": ("🗓 This month summary", "this month summary", get_this_month_range),
    "last_month": ("🗓 Last month summary", "last month summary", get_last_month_range),
}


async def _send_text(
    target: Message | CallbackQuery,
    text: str,
    *,
    edit_callback_message: bool = False,
) -> None:
    if isinstance(target, CallbackQuery):
        if (
            edit_callback_message
            and target.message is not None
            and hasattr(target.message, "edit_text")
        ):
            await target.message.edit_text(text)
        elif target.message is not None and hasattr(target.message, "answer"):
            await target.message.answer(text)
        else:
            await target.answer(text[:200], show_alert=True)
            return
        await target.answer()
        return

    await target.answer(text)


async def send_manager_report_summary(
    target: Message | CallbackQuery,
    preset_name: str,
    *,
    edit_callback_message: bool = False,
) -> None:
    preset = REPORT_PRESETS.get(preset_name)
    if preset is None:
        await _send_text(
            target,
            "Unknown report period.",
            edit_callback_message=edit_callback_message,
        )
        return

    title, log_label, range_factory = preset
    user = target.from_user
    user_id = user.id if user else None
    if user_id is None or not is_manager(user_id):
        if isinstance(target, CallbackQuery):
            await target.answer("Access denied.", show_alert=True)
        else:
            await target.answer("Access denied.")
        return

    from_date, to_date = range_factory()

    try:
        report = await get_admin_report_summary(
            from_date=from_date,
            to_date=to_date,
        )
    except BackendAPIError as exc:
        logger.warning("Could not load %s: %s", log_label, exc)
        detail = str(exc)
        message = (
            "Backend is unavailable. Please try again later."
            if detail == "Backend is unavailable. Please try again later."
            else "Could not load summary. Please try again."
        )
        await _send_text(
            target,
            message,
            edit_callback_message=edit_callback_message,
        )
        return
    except Exception:
        logger.exception("Unexpected error while loading %s", log_label)
        await _send_text(
            target,
            "Backend is unavailable. Please try again later.",
            edit_callback_message=edit_callback_message,
        )
        return

    text = format_report_summary(report, title, scope_label="All masters")
    await _send_text(target, text, edit_callback_message=edit_callback_message)


async def send_report_summary(
    target: Message | CallbackQuery,
    preset_name: str,
    *,
    edit_callback_message: bool = False,
) -> None:
    await send_manager_report_summary(
        target,
        preset_name,
        edit_callback_message=edit_callback_message,
    )


@router.message(Command("today_summary"))
async def today_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "today")


@router.message(Command("yesterday_summary"))
async def yesterday_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "yesterday")


@router.message(Command("this_week_summary"))
async def this_week_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "this_week")


@router.message(Command("last_week_summary"))
async def last_week_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "last_week")


@router.message(Command("this_month_summary"))
async def this_month_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "this_month")


@router.message(Command("last_month_summary"))
async def last_month_summary_command(message: Message) -> None:
    await send_manager_report_summary(message, "last_month")


@router.callback_query(F.data == "manager_report:today")
async def today_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "today", edit_callback_message=True)


@router.callback_query(F.data == "manager_report:yesterday")
async def yesterday_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "yesterday", edit_callback_message=True)


@router.callback_query(F.data == "manager_report:this_week")
async def this_week_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "this_week", edit_callback_message=True)


@router.callback_query(F.data == "manager_report:last_week")
async def last_week_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "last_week", edit_callback_message=True)


@router.callback_query(F.data == "manager_report:this_month")
async def this_month_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "this_month", edit_callback_message=True)


@router.callback_query(F.data == "manager_report:last_month")
async def last_month_summary_callback(callback: CallbackQuery) -> None:
    await send_manager_report_summary(callback, "last_month", edit_callback_message=True)


@router.callback_query(F.data.startswith("report:"))
async def legacy_report_callback(callback: CallbackQuery) -> None:
    preset_name = callback.data.split(":", 1)[1] if callback.data else ""
    await send_manager_report_summary(callback, preset_name, edit_callback_message=True)
