import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import get_smtp_config

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> bool:
    config = get_smtp_config()
    host = str(config.get("host") or "").strip()
    username = str(config.get("username") or "").strip()
    password = str(config.get("password") or "")
    from_email = str(config.get("from_email") or "").strip()
    from_name = str(config.get("from_name") or "Salon Booking").strip()

    if not host or not username or not password or not from_email:
        logger.warning("[EMAIL] Booking confirmation skipped: SMTP config missing")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((from_name, from_email))
    message["To"] = to_email
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    port = int(config.get("port") or 587)
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)

    return True
