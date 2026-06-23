import { useCallback, useEffect, useState } from 'react'
import { sendAIMessage } from '../api/aiAssistantApi'
import type { AIChatContextMessage, AIChatMessage, BookingDraft, BookingIntentResponse } from '../types'

const unavailableMessage = 'AI assistant is temporarily unavailable right now, but the booking system is still working normally. You can continue by using the booking form.'
const maxContextMessages = 8

function createMessage(
  role: AIChatMessage['role'],
  text: string,
  metadata?: BookingIntentResponse,
  action?: AIChatMessage['action']
): AIChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    text,
    createdAt: new Date().toISOString(),
    action,
    metadata,
  }
}

function createInitialMessages(): AIChatMessage[] {
  return [
    createMessage('assistant', "Hi! I'm your booking assistant. How can I help you today?"),
  ]
}

function buildConversationContext(
  messages: AIChatMessage[],
  nextUserMessage: string
): AIChatContextMessage[] {
  return [
    ...messages.map(message => ({
      role: message.role,
      content: message.text,
    })),
    {
      role: 'user' as const,
      content: nextUserMessage,
    },
  ].slice(-maxContextMessages)
}

export function useAIChatWidget() {
  const [isOpen, setIsOpen] = useState(true)
  const [messages, setMessages] = useState<AIChatMessage[]>(createInitialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentBookingDraft, setCurrentBookingDraft] = useState<BookingDraft | null>(null)

  const closeWidget = useCallback(() => setIsOpen(false), [])
  const toggleWidget = useCallback(() => setIsOpen(prev => !prev), [])

  const sendMessage = useCallback(async () => {
    const nextMessage = inputValue.trim()

    if (!nextMessage || isLoading) return

    const conversationContext = buildConversationContext(messages, nextMessage)
    setMessages(prev => [...prev, createMessage('user', nextMessage)])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await sendAIMessage(
        nextMessage,
        conversationContext,
        currentBookingDraft
      )
      setCurrentBookingDraft(response.booking_draft)
      setMessages(prev => [
        ...prev,
        createMessage('assistant', response.assistant_message, response),
      ])
    } catch {
      setMessages(prev => [
        ...prev,
        createMessage('assistant', unavailableMessage, undefined, 'book_manually'),
      ])
    } finally {
      setIsLoading(false)
    }
  }, [currentBookingDraft, inputValue, isLoading, messages])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeWidget()
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [closeWidget])

  return {
    isOpen,
    messages,
    inputValue,
    isLoading,
    setInputValue,
    closeWidget,
    toggleWidget,
    sendMessage,
  }
}
