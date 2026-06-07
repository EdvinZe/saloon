from app.core.database import Base, engine
from app.modules.bookings.models import Booking
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from app.modules.telegram_accounts.models import TelegramAccount


def init_db() -> None:
    # Development only: create local SQLite tables until Alembic is added.
    _ = Service, Master, MasterService, MasterShift, Booking, TelegramAccount
    Base.metadata.create_all(bind=engine)
