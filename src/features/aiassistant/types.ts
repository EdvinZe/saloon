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
  missing_fields: string[]
  assistant_message: string
}

export interface AIChatMessage {
  id: string
  role: AIChatRole
  text: string
  createdAt: string
  action?: 'book_manually'
  metadata?: BookingIntentResponse
}
