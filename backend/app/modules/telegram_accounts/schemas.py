from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

TelegramAccountRole = Literal["manager", "barber"]


class TelegramAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    role: TelegramAccountRole
    first_name: str
    last_name: str | None
    master_id: int | None
    master: Any | None = Field(default=None, exclude=True)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def master_name(self) -> str | None:
        master = getattr(self, "master", None)
        if master is None:
            return None
        return f"{master.first_name} {master.last_name}"


class TelegramAccountCreate(BaseModel):
    telegram_id: int
    role: str = Field(min_length=1)
    first_name: str = Field(min_length=1)
    last_name: str | None = None
    master_id: int | None = None
    is_active: bool = True


class TelegramAccountUpdate(BaseModel):
    telegram_id: int | None = None
    role: str | None = Field(default=None, min_length=1)
    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = None
    master_id: int | None = None
    is_active: bool | None = None
