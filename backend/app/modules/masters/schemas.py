from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MasterServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MasterPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str = Field(exclude=True)
    last_name: str = Field(exclude=True)
    role: str
    bio: str
    initials: str
    services: list[MasterServicePublic]

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class MasterAdmin(MasterPublic):
    first_name: str
    last_name: str
    birth_date: date | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class MasterCreate(BaseModel):
    first_name: str
    last_name: str
    role: str
    bio: str = ""
    initials: str
    birth_date: date | None = None
    is_active: bool = True
    sort_order: int = 0
    service_ids: list[int] = Field(default_factory=list)


class AdminMasterServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal = Field(exclude=True)
    duration_minutes: int
    cleanup_time_minutes: int
    is_active: bool

    @computed_field
    @property
    def price_cents(self) -> int:
        return int(
            (self.price * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )


class AdminMasterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    role: str
    bio: str
    initials: str
    birth_date: date | None
    is_active: bool
    sort_order: int
    services: list[AdminMasterServiceRead]
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AdminMasterCreate(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    role: str = Field(default="", min_length=1)
    bio: str = ""
    initials: str = Field(min_length=1)
    birth_date: date | None = None
    is_active: bool = True
    sort_order: int = 0
    service_ids: list[int] = Field(default_factory=list)


class AdminMasterUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    role: str | None = Field(default=None, min_length=1)
    bio: str | None = None
    initials: str | None = Field(default=None, min_length=1)
    birth_date: date | None = None
    is_active: bool | None = None
    sort_order: int | None = None
    service_ids: list[int] | None = None


class AdminMasterServicesUpdate(BaseModel):
    service_ids: list[int] = Field(default_factory=list)
