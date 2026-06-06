from dataclasses import dataclass

from telegram_bot.config import load_config


@dataclass(frozen=True)
class BotUserContext:
    telegram_user_id: int
    role: str
    master_id: int | None
    scope: str


def resolve_bot_user(user_id: int) -> BotUserContext | None:
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


def is_manager(user_id: int) -> bool:
    context = resolve_bot_user(user_id)
    return context is not None and context.role == "manager"


def is_barber(user_id: int) -> bool:
    context = resolve_bot_user(user_id)
    return context is not None and context.role == "barber"


def get_barber_master_id(user_id: int) -> int | None:
    context = resolve_bot_user(user_id)
    return context.master_id if context is not None and context.role == "barber" else None


def get_user_role(user_id: int) -> str | None:
    context = resolve_bot_user(user_id)
    return context.role if context is not None else None


def is_authorized(user_id: int) -> bool:
    return resolve_bot_user(user_id) is not None
