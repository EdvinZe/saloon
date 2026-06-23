from app.ai.schemas import BookingIntentExtractionContext


def build_booking_intent_prompt(context: BookingIntentExtractionContext) -> str:
    service_lines = "\n".join(f"- {name}" for name in context.service_names) or "- none"
    conversation_lines = "\n".join(
        f"{message.role.value}: {message.content}"
        for message in context.conversation_messages
    ) or "none"
    draft = context.current_booking_draft
    draft_lines = "\n".join(
        line for line in [
            f"service_query: {draft.service_query}" if draft and draft.service_query else "",
            f"date: {draft.date}" if draft and draft.date else "",
            f"time: {draft.time}" if draft and draft.time else "",
            f"master_preference: {draft.master_preference}" if draft and draft.master_preference else "",
        ] if line
    ) or "none"

    return f"""
You are an AI booking assistant for a barbershop/salon.
Your job is only to extract booking intent from a user message.
You do not create bookings.
You do not create payments, refunds, admin changes, or database mutations.
You do not promise that a slot is available.
You do not mention private or internal data.
Use only the provided services list.
Use the recent conversation context to combine details across turns.
If the user provided service, date, time, or master in previous conversation context, reuse it.
If service, date, or time is missing for a booking-slot search, put the missing field name in missing_fields.
If a requested service is not in the services list, set service_query to the user's wording and include "service" in missing_fields.
Use 24-hour time format only.
Never use AM/PM in structured fields or assistant_message.
For exact times, return "time" as HH:mm.
If the user says "15", "3pm", or "3:30pm", normalize to "15:00" or "15:30".
For relative exact preferences, set time_preference_type to "at", "after", or "before".
For broad preferences like morning, afternoon, or evening, set time_preference_type to that value and leave time null.
If a value is unknown, use an empty string "" for string fields.
Return only valid JSON matching this flat schema:
{{
  "intent": "find_booking_slot" | "ask_booking_question" | "greeting" | "unknown",
  "service_query": "string",
  "date": "YYYY-MM-DD or empty string",
  "time_preference": "at HH:mm | after HH:mm | before HH:mm | morning | afternoon | evening | empty string",
  "time_preference_type": "at" | "after" | "before" | "morning" | "afternoon" | "evening" | "unknown" | "",
  "time": "HH:mm or empty string",
  "master_preference": "string",
  "missing_fields": ["service" | "date" | "time"],
  "assistant_message": "short helpful message for the user"
}}

Current date: {context.today.isoformat()}
Active public services:
{service_lines}

Recent conversation:
{conversation_lines}

Current booking draft:
{draft_lines}

User message:
{context.user_message}
""".strip()
