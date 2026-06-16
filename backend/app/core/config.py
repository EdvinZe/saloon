import os
import secrets

from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


SMTP_PORT = _parse_int(os.getenv("SMTP_PORT"), 587)
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "").strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Salon Booking").strip() or "Salon Booking"
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
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_SESSION_SECRET = os.getenv("ADMIN_SESSION_SECRET", "")
ADMIN_SESSION_EXPIRE_MINUTES = _parse_int(
    os.getenv("ADMIN_SESSION_EXPIRE_MINUTES"),
    1440,
)
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
    return CORS_ALLOWED_ORIGINS or ["http://localhost:5173"]


def get_smtp_config() -> dict[str, str | int]:
    return {
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "username": SMTP_USERNAME,
        "password": SMTP_PASSWORD,
        "from_email": SMTP_FROM_EMAIL,
        "from_name": SMTP_FROM_NAME,
    }


def is_production() -> bool:
    return APP_ENV in {"production", "prod"}


def get_admin_session_secret() -> str:
    if ADMIN_SESSION_SECRET:
        return ADMIN_SESSION_SECRET
    if is_production():
        raise RuntimeError("ADMIN_SESSION_SECRET is not configured")
    return _DEV_ADMIN_SESSION_SECRET
