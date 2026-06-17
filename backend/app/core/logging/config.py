import logging.config
import re

from app.core.config import get_log_level, is_production

LOG_FORMAT = "[{levelname}] {asctime} {name}: {message}"

_REDACTION_PATTERNS = [
    re.compile(r"bot[0-9]+:[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE),
    re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9_]+"),
    re.compile(r"\bwhsec_[A-Za-z0-9_]+"),
    re.compile(r"\bre_[A-Za-z0-9_]+"),
]


class SecretRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for pattern in _REDACTION_PATTERNS:
            message = pattern.sub("<redacted>", message)
        record.msg = message
        record.args = ()
        return True


def _normalize_level(level: str | None) -> str:
    candidate = (level or get_log_level()).strip().upper()
    if isinstance(logging.getLevelName(candidate), int):
        return candidate
    return "INFO"


def setup_logging(level: str | None = None) -> None:
    log_level = _normalize_level(level)
    formatter_name = "simple" if is_production() else "color"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": LOG_FORMAT,
                    "style": "{",
                },
                "color": {
                    "()": "app.core.logging.formatters.ColorFormatter",
                    "format": LOG_FORMAT,
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter_name,
                    "filters": ["redact_secrets"],
                },
            },
            "filters": {
                "redact_secrets": {
                    "()": "app.core.logging.config.SecretRedactionFilter",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
            "loggers": {
                "httpx": {
                    "level": "WARNING",
                    "propagate": True,
                },
                "httpcore": {
                    "level": "WARNING",
                    "propagate": True,
                },
                "uvicorn": {
                    "level": "INFO",
                    "propagate": True,
                },
                "uvicorn.error": {
                    "level": "INFO",
                    "propagate": True,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "propagate": True,
                },
            },
        }
    )
