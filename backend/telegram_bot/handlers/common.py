import logging

from aiogram.types import CallbackQuery, Message

from telegram_bot.auth import BotUserContext, resolve_bot_user

logger = logging.getLogger(__name__)


async def get_authorized_context(
    target: Message | CallbackQuery,
) -> BotUserContext | None:
    user_id = target.from_user.id if target.from_user else None
    context = resolve_bot_user(user_id) if user_id is not None else None

    if context is not None:
        logger.info(
            "[BOT] Authorized user: telegram_user_id=%s role=%s scope=%s master_id=%s",
            context.telegram_user_id,
            context.role,
            context.scope,
            context.master_id,
        )
        return context

    logger.warning("[BOT] Access denied: telegram_user_id=%s", user_id)
    if isinstance(target, CallbackQuery):
        await target.answer("Access denied.", show_alert=True)
    else:
        await target.answer("Access denied.")
    return None
