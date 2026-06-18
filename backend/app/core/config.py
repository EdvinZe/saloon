import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "").strip()
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Saloon Booking").strip() or "Saloon Booking"


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


PUBLIC_FRONTEND_URL = (
    os.getenv("PUBLIC_FRONTEND_URL", "http://localhost:5173").strip()
    or "http://localhost:5173"
)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
APP_ENV = os.getenv("APP_ENV", "development").strip().lower() or "development"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
AUTO_CREATE_TABLES = (
    os.getenv("AUTO_CREATE_TABLES", "true").strip().lower()
    in {"1", "true", "yes", "on"}
)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_SESSION_SECRET = os.getenv("ADMIN_SESSION_SECRET", "")
ADMIN_SESSION_EXPIRE_MINUTES = _parse_int(
    os.getenv("ADMIN_SESSION_EXPIRE_MINUTES"),
    1440,
)
CLIENT_MANAGE_CUTOFF_HOURS = max(
    0,
    _parse_int(os.getenv("CLIENT_MANAGE_CUTOFF_HOURS"), 12),
)
RATE_LIMIT_ENABLED = _parse_bool(os.getenv("RATE_LIMIT_ENABLED"), True)
_DEV_ADMIN_SESSION_SECRET = secrets.token_urlsafe(32)


def require_stripe_secret_key() -> str:
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    return STRIPE_SECRET_KEY


def require_stripe_webhook_secret() -> str:
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured")
    return STRIPE_WEBHOOK_SECRET


def get_public_frontend_url() -> str:
    return PUBLIC_FRONTEND_URL.rstrip("/")


def get_cors_allowed_origins() -> list[str]:
    allowed_origins = [origin for origin in CORS_ALLOWED_ORIGINS if origin != "*"]
    if allowed_origins:
        return allowed_origins

    if is_production():
        logger.warning(
            "[CONFIG] CORS_ALLOWED_ORIGINS is empty or unsafe in production; "
            "cross-origin browser requests will be denied"
        )
        return []

    return ["http://localhost:5173"]


def get_client_manage_cutoff_hours() -> int:
    return CLIENT_MANAGE_CUTOFF_HOURS


def get_email_config() -> dict[str, str]:
    return {
        "resend_api_key": RESEND_API_KEY,
        "from_email": EMAIL_FROM,
        "from_name": EMAIL_FROM_NAME,
    }


def is_production() -> bool:
    return APP_ENV in {"production", "prod"}


def get_log_level() -> str:
    return LOG_LEVEL


def should_auto_create_tables() -> bool:
    return AUTO_CREATE_TABLES


def get_admin_session_secret() -> str:
    if ADMIN_SESSION_SECRET:
        return ADMIN_SESSION_SECRET
    if is_production():
        raise RuntimeError("ADMIN_SESSION_SECRET is not configured")
    return _DEV_ADMIN_SESSION_SECRET
