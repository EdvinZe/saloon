from datetime import date, datetime

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
