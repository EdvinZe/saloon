from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, computed_field


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
        return self.duration_minutes + self.cleanup_time_minutes


class ServiceAdmin(ServicePublic):
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
