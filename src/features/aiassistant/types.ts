export type AIChatRole = 'assistant' | 'user'

export interface BookingIntentResponse {
  intent: string
  service_query: string | null
  date: string | null
  time_preference: string | null
  master_preference: string | null
  missing_fields: string[]
  assistant_message: string
}

export interface AIChatMessage {
  id: string
  role: AIChatRole
  text: string
  timestamp: string
  metadata?: BookingIntentResponse
}
