import logging

from app.core.database import Base, engine
from app.modules.bookings.models import Booking
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from app.modules.telegram_accounts.models import TelegramAccount

logger = logging.getLogger(__name__)


def init_db() -> None:
    # Demo/local deployment path until migrations are introduced.
    _ = Service, Master, MasterService, MasterShift, Booking, TelegramAccount
    Base.metadata.create_all(bind=engine)
    logger.info("[STARTUP] Database tables ensured")
