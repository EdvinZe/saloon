import logging


class ColorFormatter(logging.Formatter):
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    PURPLE = "\033[35m"
    RESET = "\033[0m"

    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: PURPLE,
    }

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = self.COLORS.get(record.levelno)
        if not color:
            return message
        return f"{color}{message}{self.RESET}"
