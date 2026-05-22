from app.core.database import Base, engine
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service


def init_db() -> None:
    # Development only: create local SQLite tables until Alembic is added.
    _ = Service, Master, MasterService
    Base.metadata.create_all(bind=engine)
