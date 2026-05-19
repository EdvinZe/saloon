from fastapi import FastAPI

from app.core.database import Base, engine
from app.modules.services.models import Service
from app.modules.services.admin_router import router as admin_services_router
from app.modules.services.router import router as services_router

app = FastAPI(title="Saloon API")

# Development only: create local SQLite tables until migrations are added.
_ = Service
Base.metadata.create_all(bind=engine)

app.include_router(
    services_router,
    prefix="/api/services",
    tags=["Services"],
)

app.include_router(
    admin_services_router,
    prefix="/api/admin/services",
    tags=["Admin Services"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
