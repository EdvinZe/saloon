from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field


class BookingCreate(BaseModel):
    service_id: int
    master_id: int
    date: date
    time: str
    customer_first_name: str = Field(min_length=1, max_length=80)
    customer_last_name: str = Field(min_length=1, max_length=80)
    customer_phone: str = Field(min_length=1, max_length=40)
    customer_email: str = Field(min_length=1, max_length=255)


class BookingAvailabilityCheckResponse(BaseModel):
    available: bool
    message: str


class BookingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_code: str | None
    manage_token: str
    service_id: int
    master_id: int
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_email: str
    start_at: datetime
    end_at: datetime
    status: str
    deposit_status: str
    source: str
    deposit_amount_cents: int
    currency: str

    @computed_field
    @property
    def manage_url(self) -> str:
        return f"/booking/manage/{self.manage_token}"


class BookingAdmin(BookingPublic):
    stripe_checkout_session_id: str | None
    stripe_payment_intent_id: str | None
    created_at: datetime
    updated_at: datetime
