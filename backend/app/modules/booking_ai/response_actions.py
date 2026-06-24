from app.modules.booking_ai.schemas import (
    BookingAssistantAction,
    BookingAssistantActionPayload,
    BookingAvailabilityOption,
)


def build_prefill_actions(
    options: list[BookingAvailabilityOption],
    *,
    use_option_labels: bool = False,
) -> list[BookingAssistantAction]:
    actions: list[BookingAssistantAction] = []
    for option in options:
        label = "Continue booking"
        if use_option_labels:
            label = f"Use {option.time}"
        elif len(options) > 1:
            label = f"Book with {option.master_name} at {option.time}"

        actions.append(
            BookingAssistantAction(
                label=label,
                payload=BookingAssistantActionPayload(
                    service_id=option.service_id,
                    master_id=option.master_id,
                    date=option.date,
                    time=option.time,
                ),
            )
        )
    return actions
