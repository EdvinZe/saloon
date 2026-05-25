from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.masters.models import Master
from app.modules.services.models import Service


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_code: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
        unique=True,
        index=True,
    )
    manage_token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
        index=True,
    )
    master_id: Mapped[int] = mapped_column(
        ForeignKey("masters.id"),
        nullable=False,
        index=True,
    )
    customer_first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    customer_last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="confirmed",
        index=True,
    )
    deposit_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="paid",
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="online",
        index=True,
    )
    deposit_amount_cents: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1000,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    service: Mapped[Service] = relationship("Service")
    master: Mapped[Master] = relationship("Master")
