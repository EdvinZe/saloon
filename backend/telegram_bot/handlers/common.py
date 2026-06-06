from aiogram.types import CallbackQuery, Message

from telegram_bot.auth import BotUserContext, resolve_bot_user


async def get_authorized_context(
    target: Message | CallbackQuery,
) -> BotUserContext | None:
    user_id = target.from_user.id if target.from_user else None
    context = resolve_bot_user(user_id) if user_id is not None else None

    if context is not None:
        return context

    if isinstance(target, CallbackQuery):
        await target.answer("Access denied.", show_alert=True)
    else:
        await target.answer("Access denied.")
    return None
