from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.auth import get_user_role

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
                ]
            )
        )
        return

    await message.answer(
        "\n".join(
            [
                "Welcome.",
                "Commands:",
                "/today - your bookings today",
                "/tomorrow - your bookings tomorrow",
            ]
        )
    )
