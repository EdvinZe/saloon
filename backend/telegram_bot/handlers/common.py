import logging

from aiogram.types import CallbackQuery, Message

from telegram_bot.api_client import BackendAPIError
from telegram_bot.auth import BotUserContext, resolve_bot_user

logger = logging.getLogger(__name__)


async def get_authorized_context(
    target: Message | CallbackQuery,
) -> BotUserContext | None:
    user_id = target.from_user.id if target.from_user else None
    try:
        context = await resolve_bot_user(user_id) if user_id is not None else None
    except BackendAPIError as exc:
        logger.warning("[BOT] Authorization backend unavailable: %s", exc)
        if isinstance(target, CallbackQuery):
            await target.answer(
                "Service is temporarily unavailable. Please try again later.",
                show_alert=True,
            )
        else:
            await target.answer("Service is temporarily unavailable. Please try again later.")
        return None
    except Exception:
        logger.exception("[BOT] Authorization failed unexpectedly")
        if isinstance(target, CallbackQuery):
            await target.answer(
                "Service is temporarily unavailable. Please try again later.",
                show_alert=True,
            )
        else:
            await target.answer("Service is temporarily unavailable. Please try again later.")
        return None

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
