from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram_bot.auth import get_user_role

router = Router()


def _next_placeholder_message(role: str) -> str:
    if role == "manager":
        return "\n\n".join(
            [
                "Next bookings view is coming soon.",
                "Soon this will show all reservations for the next 2 hours.",
            ]
        )
    if role == "barber":
        return "\n\n".join(
            [
                "Next bookings view is coming soon.",
                "Soon this will show your reservations for the next 2 hours.",
            ]
        )
    return "Access denied."


async def _send_next_placeholder(target: Message | CallbackQuery) -> None:
    user_id = target.from_user.id if target.from_user else None
    role = get_user_role(user_id) if user_id is not None else None

    if role not in {"manager", "barber"}:
        if isinstance(target, CallbackQuery):
            await target.answer("Access denied.", show_alert=True)
        else:
            await target.answer("Access denied.")
        return

    text = _next_placeholder_message(role)
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await target.message.answer(text)
        else:
            await target.answer(text[:200], show_alert=True)
        await target.answer()
        return

    await target.answer(text)


@router.message(Command("next"))
async def next_command(message: Message) -> None:
    await _send_next_placeholder(message)


@router.callback_query(F.data == "next_placeholder")
async def next_placeholder_callback(callback: CallbackQuery) -> None:
    await _send_next_placeholder(callback)
