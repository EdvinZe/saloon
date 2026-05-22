import logging.config

LOG_FORMAT = "[{levelname}] {asctime} {name}: {message}"


def setup_logging(debug: bool = True) -> None:
    formatter_name = "color" if debug else "simple"

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
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "loggers": {
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
