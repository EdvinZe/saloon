from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.auth import is_manager
from telegram_bot.keyboards import report_summary_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None

    if user_id is None or not is_manager(user_id):
        await message.answer("Access denied.")
        return

    await message.answer(
        "\n".join(
            [
                "Welcome, manager.",
                "Commands:",
                "/today - all bookings today",
                "/tomorrow - all bookings tomorrow",
                "/today_summary - today's summary",
                "/yesterday_summary - yesterday's summary",
                "/this_week_summary - this week's summary",
                "/last_week_summary - last week's summary",
                "/this_month_summary - this month's summary",
                "/last_month_summary - last month's summary",
            ]
        ),
        reply_markup=report_summary_keyboard(),
    )
