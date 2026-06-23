import { useCallback, useEffect, useState } from 'react'
import { sendAIMessage } from '../api/aiAssistantApi'
import type { AIChatMessage, BookingIntentResponse } from '../types'

const initialMessages: AIChatMessage[] = [
  {
    id: 'assistant-1',
    role: 'assistant',
    text: "Hi! I'm your booking assistant. How can I help you today?",
    timestamp: 'Now',
  },
  {
    id: 'user-1',
    role: 'user',
    text: "Hi, I'd like to book a haircut.",
    timestamp: 'Now',
  },
  {
    id: 'assistant-2',
    role: 'assistant',
    text: 'Great! What date and time works best for you?',
    timestamp: 'Now',
  },
  {
    id: 'user-2',
    role: 'user',
    text: 'Tomorrow after 3pm.',
    timestamp: 'Now',
  },
  {
    id: 'assistant-3',
    role: 'assistant',
    text: 'I can help you find matching booking options.',
    timestamp: 'Now',
  },
]

const unavailableMessage = 'AI assistant is temporarily unavailable. Please try again in a moment.'

function createMessage(
  role: AIChatMessage['role'],
  text: string,
  metadata?: BookingIntentResponse
): AIChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    text,
    timestamp: 'Now',
    metadata,
  }
}

export function useAIChatWidget() {
  const [isOpen, setIsOpen] = useState(true)
  const [messages, setMessages] = useState<AIChatMessage[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const closeWidget = useCallback(() => setIsOpen(false), [])
  const toggleWidget = useCallback(() => setIsOpen(prev => !prev), [])

  const sendMessage = useCallback(async () => {
    const nextMessage = inputValue.trim()

    if (!nextMessage || isLoading) return

    setMessages(prev => [...prev, createMessage('user', nextMessage)])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await sendAIMessage(nextMessage)
      setMessages(prev => [
        ...prev,
        createMessage('assistant', response.assistant_message, response),
      ])
    } catch {
      setMessages(prev => [...prev, createMessage('assistant', unavailableMessage)])
    } finally {
      setIsLoading(false)
    }
  }, [inputValue, isLoading])

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
