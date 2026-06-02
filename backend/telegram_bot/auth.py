from telegram_bot.config import load_config


def is_manager(user_id: int) -> bool:
    return user_id in load_config().manager_ids


def get_barber_master_id(user_id: int) -> int | None:
    return load_config().barber_master_map.get(user_id)


def get_user_role(user_id: int) -> str | None:
    if is_manager(user_id):
        return "manager"
    if get_barber_master_id(user_id) is not None:
        return "barber"
    return None


def is_authorized(user_id: int) -> bool:
    return get_user_role(user_id) is not None
