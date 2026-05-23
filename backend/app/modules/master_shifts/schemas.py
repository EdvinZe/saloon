from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class MasterShiftCreate(BaseModel):
    master_id: int
    date: date
    start_time: time | None = None
    end_time: time | None = None
    status: str = "working"
    note: str | None = None


class MasterShiftUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    status: str | None = None
    note: str | None = None


class MasterShiftAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shift_code: str
    master_id: int
    date: date
    start_time: time | None
    end_time: time | None
    status: str
    note: str | None
    created_at: datetime
    updated_at: datetime
