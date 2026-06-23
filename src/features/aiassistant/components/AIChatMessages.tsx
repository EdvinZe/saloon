import { useEffect, useRef } from 'react'
import type { AIChatMessage, BookingAssistantAction } from '../types'

interface AIChatMessagesProps {
  messages: AIChatMessage[]
  isLoading: boolean
  onBookManually: () => void
  onAssistantAction: (action: BookingAssistantAction) => void
}

function formatChatTime(createdAt: string): string {
  const date = new Date(createdAt)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${hours}:${minutes}`
}

export default function AIChatMessages({
  messages,
  isLoading,
  onBookManually,
  onAssistantAction,
}: AIChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isLoading])

  return (
    <div className="ai-chat-messages" role="log" aria-live="polite" aria-label="Booking assistant messages">
      {messages.map(message => (
        <article
          key={message.id}
          className={`ai-chat-message ai-chat-message-${message.role}`}
        >
          <div className="ai-chat-bubble">{message.text}</div>
          {message.action === 'book_manually' && (
            <button
              type="button"
              className="ai-chat-message-action"
              onClick={onBookManually}
            >
              Book manually
            </button>
          )}
          {message.role === 'assistant' && message.metadata?.actions?.map((action, index) => (
            <button
              key={`${message.id}-${action.type}-${index}`}
              type="button"
              className="ai-chat-message-action"
              onClick={() => onAssistantAction(action)}
            >
              {action.label}
            </button>
          ))}
          <time className="ai-chat-message-meta" dateTime={message.createdAt}>
            {formatChatTime(message.createdAt)}
          </time>
        </article>
      ))}

      {isLoading && (
        <article className="ai-chat-message ai-chat-message-assistant">
          <div className="ai-chat-bubble ai-chat-bubble-loading" aria-label="Assistant is typing">
            <span />
            <span />
            <span />
          </div>
        </article>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}
