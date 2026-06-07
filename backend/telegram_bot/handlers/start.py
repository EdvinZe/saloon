from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import barber_start_keyboard, manager_start_keyboard

router = Router()


def get_manager_menu_text() -> str:
    return "\n".join(
        [
            "Welcome, manager.",
            "Commands:",
            "/menu - show main menu",
            "/today - all bookings today",
            "/tomorrow - all bookings tomorrow",
            "/now - current salon status",
            "/next - upcoming reservations, coming soon",
            "/today_summary - today's summary",
            "/yesterday_summary - yesterday's summary",
            "/this_week_summary - this week's summary",
            "/last_week_summary - last week's summary",
            "/this_month_summary - this month's summary",
            "/last_month_summary - last month's summary",
        ]
    )


def get_barber_menu_text() -> str:
    return "\n".join(
        [
            "Welcome.",
            "Commands:",
            "/menu - show main menu",
            "/today - your bookings today",
            "/tomorrow - your bookings tomorrow",
            "/now - your current status",
            "/next - upcoming reservations, coming soon",
        ]
    )


async def send_main_menu(target: Message | CallbackQuery) -> None:
    ctx = await get_authorized_context(target)
    if ctx is None:
        return

    if ctx.role == "barber":
        text = get_barber_menu_text()
        reply_markup = barber_start_keyboard()
    else:
        text = get_manager_menu_text()
        reply_markup = manager_start_keyboard()

    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.answer(text, reply_markup=reply_markup)
        else:
            await target.answer(text[:200], show_alert=True)
            return
        await target.answer()
        return

    await target.answer(text, reply_markup=reply_markup)


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await send_main_menu(message)


@router.message(Command("menu"))
async def menu_command(message: Message) -> None:
    await send_main_menu(message)


@router.callback_query(F.data == "manager_menu")
async def manager_menu_callback(callback: CallbackQuery) -> None:
    await send_main_menu(callback)
