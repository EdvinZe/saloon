from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.services.models import Service


class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    initials: Mapped[str] = mapped_column(String(10), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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

    service_links: Mapped[list["MasterService"]] = relationship(
        "MasterService",
        back_populates="master",
        cascade="all, delete-orphan",
    )

    @property
    def services(self) -> list[Service]:
        return [link.service for link in self.service_links]


class MasterService(Base):
    __tablename__ = "master_services"
    __table_args__ = (
        UniqueConstraint("master_id", "service_id", name="uq_master_service"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    master: Mapped[Master] = relationship("Master", back_populates="service_links")
    service: Mapped[Service] = relationship("Service")
