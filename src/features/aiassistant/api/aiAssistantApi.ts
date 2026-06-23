import type { AIChatContextMessage, BookingDraft, BookingIntentResponse } from '../types'

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

export interface BookingIntentRequest {
  message: string
  messages?: AIChatContextMessage[]
  current_booking_draft?: BookingDraft | null
}

export async function sendAIMessage(
  message: string,
  messages?: AIChatContextMessage[],
  currentBookingDraft?: BookingDraft | null
): Promise<BookingIntentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ai/booking-intent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      messages,
      current_booking_draft: currentBookingDraft,
    } satisfies BookingIntentRequest),
  })

  if (!response.ok) {
    throw new Error('Failed to send AI assistant message')
  }

  return response.json() as Promise<BookingIntentResponse>
}
