from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    duration_minutes: int
    cleanup_time_minutes: int = 15
    price: Decimal
    is_active: bool = True
    sort_order: int = 0


class ServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    duration_minutes: int
    cleanup_time_minutes: int
    price: Decimal

    @computed_field
    @property
    def total_duration_minutes(self) -> int:
        return self.duration_minutes + (self.cleanup_time_minutes or 0)


class ServiceAdmin(ServicePublic):
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class AdminServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: Decimal = Field(exclude=True)
    duration_minutes: int
    cleanup_time_minutes: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def price_cents(self) -> int:
        return int(
            (self.price * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

    @computed_field
    @property
    def total_duration_minutes(self) -> int:
        return self.duration_minutes + (self.cleanup_time_minutes or 0)


class AdminServiceCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""
    price_cents: int = Field(ge=0)
    duration_minutes: int = Field(gt=0)
    cleanup_time_minutes: int = Field(default=15, ge=0)
    is_active: bool = True
    sort_order: int = 0


class AdminServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    cleanup_time_minutes: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    sort_order: int | None = None
