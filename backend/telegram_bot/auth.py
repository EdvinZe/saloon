from dataclasses import dataclass

from telegram_bot.api_client import resolve_telegram_account
from telegram_bot.config import load_config


@dataclass(frozen=True)
class BotUserContext:
    telegram_user_id: int
    role: str
    master_id: int | None
    scope: str
    first_name: str | None = None
    last_name: str | None = None
    master_name: str | None = None


async def resolve_bot_user(user_id: int) -> BotUserContext | None:
    config = load_config()

    if config.telegram_auth_source == "env":
        return _resolve_bot_user_from_env(user_id)

    payload = await resolve_telegram_account(user_id)
    if payload.get("authorized") is not True:
        return None

    role = payload.get("role")
    scope = payload.get("scope")
    master_id = payload.get("master_id")
    first_name = _optional_text(payload.get("first_name"))
    last_name = _optional_text(payload.get("last_name"))
    master_name = _optional_text(payload.get("master_name"))

    if role == "manager" and scope == "all":
        return BotUserContext(
            telegram_user_id=user_id,
            role="manager",
            master_id=None,
            scope="all",
            first_name=first_name,
            last_name=last_name,
            master_name=master_name,
        )

    if role == "barber" and scope == "own_master" and master_id is not None:
        try:
            parsed_master_id = int(master_id)
        except (TypeError, ValueError):
            return None
        return BotUserContext(
            telegram_user_id=user_id,
            role="barber",
            master_id=parsed_master_id,
            scope="own_master",
            first_name=first_name,
            last_name=last_name,
            master_name=master_name,
        )

    return None


def _optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _resolve_bot_user_from_env(user_id: int) -> BotUserContext | None:
    config = load_config()

    if user_id in config.manager_ids:
        return BotUserContext(
            telegram_user_id=user_id,
            role="manager",
            master_id=None,
            scope="all",
        )

    master_id = config.barber_master_map.get(user_id)
    if master_id is not None:
        return BotUserContext(
            telegram_user_id=user_id,
            role="barber",
            master_id=master_id,
            scope="own_master",
        )

    return None


async def is_manager(user_id: int) -> bool:
    context = await resolve_bot_user(user_id)
    return context is not None and context.role == "manager"


async def is_barber(user_id: int) -> bool:
    context = await resolve_bot_user(user_id)
    return context is not None and context.role == "barber"


async def get_barber_master_id(user_id: int) -> int | None:
    context = await resolve_bot_user(user_id)
    return context.master_id if context is not None and context.role == "barber" else None


async def get_user_role(user_id: int) -> str | None:
    context = await resolve_bot_user(user_id)
    return context.role if context is not None else None


async def is_authorized(user_id: int) -> bool:
    return await resolve_bot_user(user_id) is not None
