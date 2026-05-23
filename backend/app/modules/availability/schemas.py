from typing import Literal

from pydantic import BaseModel


class AvailableSlotStatus(BaseModel):
    time: str
    status: Literal["free", "tooShort"]
