export type AIChatRole = 'assistant' | 'user'

export interface AIChatContextMessage {
  role: AIChatRole
  content: string
}

export interface BookingIntentResponse {
  intent: string
  service_query: string | null
  date: string | null
  time_preference: string | null
  time_preference_type: 'at' | 'after' | 'before' | 'morning' | 'afternoon' | 'evening' | 'unknown' | null
  time: string | null
  master_preference: string | null
  booking_draft: BookingDraft
  missing_fields: string[]
  next_action: string
  assistant_message: string
  requested_time_available: boolean | null
  available_options: BookingAvailabilityOption[]
  nearest_options: BookingNearestAvailabilityOption[]
  actions: BookingAssistantAction[]
}

export interface BookingDraft {
  service_query: string | null
  service_id?: number | null
  date: string | null
  time: string | null
  time_preference: string | null
  time_preference_type: 'at' | 'after' | 'before' | 'morning' | 'afternoon' | 'evening' | 'unknown' | null
  master_preference: string | null
  master_id?: number | null
  master_name?: string | null
}

export interface BookingAvailabilityOption {
  service_id: number
  service_name: string
  master_id: number
  master_name: string
  date: string
  time: string
}

export interface BookingNearestAvailabilityOption extends BookingAvailabilityOption {
  direction: string
}

export interface BookingAssistantActionPayload {
  service_id: number
  master_id: number
  date: string
  time: string
}

export interface BookingAssistantAction {
  type: 'prefill_booking'
  label: string
  payload: BookingAssistantActionPayload
}

export interface AIChatMessage {
  id: string
  role: AIChatRole
  text: string
  createdAt: string
  action?: 'book_manually'
  metadata?: BookingIntentResponse
}
