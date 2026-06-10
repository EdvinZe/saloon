import os
import logging
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotConfig:
    telegram_bot_token: str
    backend_api_url: str
    telegram_auth_source: str
    manager_ids: set[int]
    barber_master_map: dict[int, int]
    bot_timezone: str
    barber_reminder_minutes: int
    barber_reminder_check_interval_seconds: int


def _parse_int_set(value: str) -> set[int]:
    parsed: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            parsed.add(int(item))
        except ValueError:
            logger.warning("[BOT] Invalid TELEGRAM_MANAGER_IDS value skipped: %s", item)
            continue
    return parsed


def _parse_int_map(value: str) -> dict[int, int]:
    parsed: dict[int, int] = {}
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            logger.warning("[BOT] Invalid TELEGRAM_BARBER_MASTER_MAP value skipped: %s", item)
            continue
        telegram_user_id, master_id = item.split(":", 1)
        try:
            parsed[int(telegram_user_id.strip())] = int(master_id.strip())
        except ValueError:
            logger.warning("[BOT] Invalid TELEGRAM_BARBER_MASTER_MAP value skipped: %s", item)
            continue
    return parsed


def _parse_positive_int(value: str, default: int, env_name: str) -> int:
    value = value.strip()
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        logger.warning("[BOT] Invalid %s value, using default: %s", env_name, default)
        return default
    if parsed <= 0:
        logger.warning("[BOT] Invalid %s value, using default: %s", env_name, default)
        return default
    return parsed


def load_config() -> BotConfig:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    backend_api_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").strip()
    if not backend_api_url:
        backend_api_url = "http://127.0.0.1:8000"

    telegram_auth_source = os.getenv("TELEGRAM_AUTH_SOURCE", "db").strip().lower()
    if telegram_auth_source not in {"db", "env"}:
        logger.warning("[BOT] Invalid TELEGRAM_AUTH_SOURCE value, using default: db")
        telegram_auth_source = "db"

    manager_ids: set[int] = set()
    barber_master_map: dict[int, int] = {}
    if telegram_auth_source == "env":
        manager_ids = _parse_int_set(os.getenv("TELEGRAM_MANAGER_IDS", ""))
        barber_master_map = _parse_int_map(os.getenv("TELEGRAM_BARBER_MASTER_MAP", ""))

    return BotConfig(
        telegram_bot_token=telegram_bot_token,
        backend_api_url=backend_api_url.rstrip("/"),
        telegram_auth_source=telegram_auth_source,
        manager_ids=manager_ids,
        barber_master_map=barber_master_map,
        bot_timezone=os.getenv("BOT_TIMEZONE", "Europe/Vilnius").strip()
        or "Europe/Vilnius",
        barber_reminder_minutes=_parse_positive_int(
            os.getenv("BARBER_REMINDER_MINUTES", ""),
            15,
            "BARBER_REMINDER_MINUTES",
        ),
        barber_reminder_check_interval_seconds=_parse_positive_int(
            os.getenv("BARBER_REMINDER_CHECK_INTERVAL_SECONDS", ""),
            60,
            "BARBER_REMINDER_CHECK_INTERVAL_SECONDS",
        ),
    )
