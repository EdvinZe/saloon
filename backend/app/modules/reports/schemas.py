from datetime import date

from pydantic import BaseModel


class AdminReportMasterSummary(BaseModel):
    master_id: int
    master_name: str
    total_bookings: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    no_show_count: int
    paid_deposits_cents: int
    refunded_deposits_cents: int
    net_deposits_cents: int


class AdminReportServiceSummary(BaseModel):
    service_id: int
    service_name: str
    total_bookings: int
    completed_count: int
    cancelled_count: int
    no_show_count: int
    paid_deposits_cents: int
    refunded_deposits_cents: int
    net_deposits_cents: int


class AdminReportDailySummary(BaseModel):
    date: date
    total_bookings: int
    completed_count: int
    cancelled_count: int
    no_show_count: int
    paid_deposits_cents: int
    refunded_deposits_cents: int
    net_deposits_cents: int


class AdminReportSummary(BaseModel):
    from_date: date
    to_date: date
    master_id: int | None
    total_bookings: int
    confirmed_count: int
    completed_count: int
    cancelled_count: int
    no_show_count: int
    paid_deposits_cents: int
    refunded_deposits_cents: int
    net_deposits_cents: int
    currency: str
    by_master: list[AdminReportMasterSummary]
    by_service: list[AdminReportServiceSummary]
    daily_breakdown: list[AdminReportDailySummary]
