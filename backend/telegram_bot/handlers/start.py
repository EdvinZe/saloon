from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.auth import get_user_role
from telegram_bot.keyboards import report_summary_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    role = get_user_role(user_id) if user_id is not None else None

    if role is None:
        await message.answer("Access denied.")
        return

    if role == "manager":
        await message.answer(
            "\n".join(
                [
                    "Welcome, manager.",
                    "Commands:",
                    "/today - all bookings today",
                    "/tomorrow - all bookings tomorrow",
                    "/today_summary - today's summary",
                    "/this_week_summary - this week's summary",
                    "/this_month_summary - this month's summary",
                ]
            ),
            reply_markup=report_summary_keyboard(),
        )
        return

    await message.answer(
        "\n".join(
            [
                "Welcome.",
                "Commands:",
                "/today - your bookings today",
                "/tomorrow - your bookings tomorrow",
                "/today_summary - today's summary",
                "/this_week_summary - this week's summary",
                "/this_month_summary - this month's summary",
            ]
        ),
        reply_markup=report_summary_keyboard(),
    )
