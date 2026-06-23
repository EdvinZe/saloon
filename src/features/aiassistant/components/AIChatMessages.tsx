import { useEffect, useRef } from 'react'
import type { AIChatMessage } from '../types'

interface AIChatMessagesProps {
  messages: AIChatMessage[]
  isLoading: boolean
}

export default function AIChatMessages({ messages, isLoading }: AIChatMessagesProps) {
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
          <time className="ai-chat-message-meta">{message.timestamp}</time>
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
