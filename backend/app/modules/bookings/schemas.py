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


class BookingDepositIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


class BookingCancelRequest(BaseModel):
    token: str


class BookingRescheduleRequest(BaseModel):
    token: str
    master_id: int
    date: date
    time: str


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
        return f"/booking/manage?token={self.manage_token}"


class ManagedBookingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_code: str | None
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


class BookingPaymentResultResponse(BaseModel):
    status: str
    message: str
    booking: BookingPublic | None = None


class BookingCancelResponse(BaseModel):
    success: bool
    message: str
    booking: ManagedBookingPublic


class BookingRescheduleResponse(BaseModel):
    success: bool
    message: str
    booking: ManagedBookingPublic


class BookingAdmin(BookingPublic):
    stripe_checkout_session_id: str | None
    stripe_payment_intent_id: str | None
    created_at: datetime
    updated_at: datetime


class AdminBookingRead(BaseModel):
    id: int
    booking_code: str | None
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
    stripe_payment_intent_id: str | None
    stripe_checkout_session_id: str | None
    created_at: datetime
    updated_at: datetime
    service_name: str | None = None
    master_name: str | None = None


class AdminBookingActionResponse(BaseModel):
    success: bool
    message: str
    booking: AdminBookingRead
