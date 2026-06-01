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


class AdminScheduleDay(BaseModel):
    date: date
    shift_id: int | None
    status: str
    start_time: str | None
    end_time: str | None
    note: str | None


class AdminScheduleMaster(BaseModel):
    id: int
    name: str
    is_active: bool
    days: list[AdminScheduleDay]


class AdminScheduleResponse(BaseModel):
    from_date: date
    to_date: date
    days: list[date]
    masters: list[AdminScheduleMaster]


class AdminScheduleDayUpsert(BaseModel):
    master_id: int
    date: date
    status: str
    start_time: str | None = None
    end_time: str | None = None
    note: str | None = None


class AdminScheduleRangeUpsert(BaseModel):
    master_id: int
    from_date: date
    to_date: date
    status: str
    start_time: str | None = None
    end_time: str | None = None
    note: str | None = None


class AdminScheduleRangeResponse(BaseModel):
    success: bool
    message: str
    updated_count: int
