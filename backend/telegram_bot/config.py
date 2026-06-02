import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    telegram_bot_token: str
    backend_api_url: str
    manager_ids: set[int]
    barber_master_map: dict[int, int]


def _parse_int_set(value: str) -> set[int]:
    parsed: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            parsed.add(int(item))
        except ValueError:
            continue
    return parsed


def _parse_int_map(value: str) -> dict[int, int]:
    parsed: dict[int, int] = {}
    for item in value.split(","):
        item = item.strip()
        if not item or ":" not in item:
            continue
        telegram_user_id, master_id = item.split(":", 1)
        try:
            parsed[int(telegram_user_id.strip())] = int(master_id.strip())
        except ValueError:
            continue
    return parsed


def load_config() -> BotConfig:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    backend_api_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").strip()
    if not backend_api_url:
        backend_api_url = "http://127.0.0.1:8000"

    return BotConfig(
        telegram_bot_token=telegram_bot_token,
        backend_api_url=backend_api_url.rstrip("/"),
        manager_ids=_parse_int_set(os.getenv("TELEGRAM_MANAGER_IDS", "")),
        barber_master_map=_parse_int_map(os.getenv("TELEGRAM_BARBER_MASTER_MAP", "")),
    )
