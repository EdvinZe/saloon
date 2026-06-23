export type AIChatRole = 'assistant' | 'user'

export interface AIChatMessage {
  id: string
  role: AIChatRole
  text: string
  timestamp: string
}
