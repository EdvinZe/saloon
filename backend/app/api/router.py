from fastapi import FastAPI

from app.modules.availability.router import router as availability_router
from app.modules.bookings.admin_router import router as admin_bookings_router
from app.modules.bookings.router import router as bookings_router
from app.modules.master_shifts.admin_router import (
    router as admin_master_shifts_router,
    schedule_router as admin_schedule_router,
)
from app.modules.masters.admin_router import router as admin_masters_router
from app.modules.masters.router import router as masters_router
from app.modules.payments.webhook_router import router as stripe_webhook_router
from app.modules.reports.admin_router import router as admin_reports_router
from app.modules.services.admin_router import router as admin_services_router
from app.modules.services.router import router as services_router
from app.modules.telegram_accounts.admin_router import (
    router as admin_telegram_accounts_router,
)


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
        bookings_router,
        prefix="/api/bookings",
        tags=["Bookings"],
    )

    app.include_router(
        stripe_webhook_router,
        prefix="/api/stripe",
        tags=["Stripe"],
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

    app.include_router(
        admin_schedule_router,
        prefix="/api/admin/schedule",
        tags=["Admin Schedule"],
    )

    app.include_router(
        admin_bookings_router,
        prefix="/api/admin/bookings",
        tags=["Admin Bookings"],
    )

    app.include_router(
        admin_reports_router,
        prefix="/api/admin/reports",
        tags=["Admin Reports"],
    )

    app.include_router(
        admin_telegram_accounts_router,
        prefix="/api/admin/telegram-accounts",
        tags=["Admin Telegram Accounts"],
    )
