export type AIChatRole = 'assistant' | 'user'

export interface AIChatContextMessage {
  role: AIChatRole
  content: string
}

export interface BookingIntentResponse {
  intent: string
  service_query: string | null
  master_query?: string | null
  date: string | null
  start_date?: string | null
  end_date?: string | null
  date_range_type?: string | null
  weekdays?: string[] | null
  time_preference: string | null
  time_preference_type: 'at' | 'exact' | 'after' | 'before' | 'between' | 'any' | 'morning' | 'afternoon' | 'evening' | 'unknown' | null
  time: string | null
  end_time?: string | null
  daypart?: string | null
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
  master_query?: string | null
  date: string | null
  start_date?: string | null
  end_date?: string | null
  date_range_type?: string | null
  weekdays?: string[] | null
  time: string | null
  end_time?: string | null
  time_preference: string | null
  time_preference_type: 'at' | 'exact' | 'after' | 'before' | 'between' | 'any' | 'morning' | 'afternoon' | 'evening' | 'unknown' | null
  daypart?: string | null
  master_preference: string | null
  master_id?: number | null
  master_name?: string | null
  last_intent?: string | null
  last_available_options?: BookingAvailabilityOption[]
  shown_option_count?: number
  excluded_master_ids?: number[]
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
  service_id?: number | null
  master_id?: number | null
  date?: string | null
  time?: string | null
  message?: string | null
}

export interface BookingAssistantAction {
  type: 'prefill_booking' | 'open_booking_form' | 'send_message' | 'reset_ai_draft'
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
