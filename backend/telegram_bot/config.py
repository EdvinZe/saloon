import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    telegram_bot_token: str
    backend_api_url: str


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
    )
