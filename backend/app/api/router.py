from fastapi import FastAPI

from app.modules.availability.router import router as availability_router
from app.modules.master_shifts.admin_router import router as admin_master_shifts_router
from app.modules.masters.admin_router import router as admin_masters_router
from app.modules.masters.router import router as masters_router
from app.modules.services.admin_router import router as admin_services_router
from app.modules.services.router import router as services_router


def register_routers(app: FastAPI) -> None:
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

    app.include_router(
        masters_router,
        prefix="/api/masters",
        tags=["Masters"],
    )

    app.include_router(
        availability_router,
        prefix="/api/availability",
        tags=["Availability"],
    )

    app.include_router(
        admin_masters_router,
        prefix="/api/admin/masters",
        tags=["Admin Masters"],
    )

    app.include_router(
        admin_master_shifts_router,
        prefix="/api/admin/master-shifts",
        tags=["Admin Master Shifts"],
    )
