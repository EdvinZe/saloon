from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.handlers.common import get_authorized_context
from telegram_bot.keyboards import barber_start_keyboard, manager_start_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    ctx = await get_authorized_context(message)
    if ctx is None:
        return

    if ctx.role == "barber":
        await message.answer(
            "\n".join(
                [
                    "Welcome.",
                    "Commands:",
                    "/today - your bookings today",
                    "/tomorrow - your bookings tomorrow",
                    "/now - your current status",
                ]
            ),
            reply_markup=barber_start_keyboard(),
        )
        return

    await message.answer(
        "\n".join(
            [
                "Welcome, manager.",
                "Commands:",
                "/today - all bookings today",
                "/tomorrow - all bookings tomorrow",
                "/now - current salon status",
                "/today_summary - today's summary",
                "/this_week_summary - this week's summary",
                "/this_month_summary - this month's summary",
            ]
        ),
        reply_markup=manager_start_keyboard(),
    )
