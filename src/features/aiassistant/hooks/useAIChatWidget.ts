import { useCallback, useEffect, useRef, useState } from 'react'
import type { AIChatMessage } from '../types'

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

const mockAssistantReply: AIChatMessage = {
  id: 'assistant-mock-reply',
  role: 'assistant',
  text: "Thanks. I'll keep this ready for booking options once AI search is connected.",
  timestamp: 'Now',
}

function createMessage(role: AIChatMessage['role'], text: string): AIChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    text,
    timestamp: 'Now',
  }
}

export function useAIChatWidget() {
  const [isOpen, setIsOpen] = useState(true)
  const [messages, setMessages] = useState<AIChatMessage[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const responseTimeoutRef = useRef<number | null>(null)

  const closeWidget = useCallback(() => setIsOpen(false), [])
  const toggleWidget = useCallback(() => setIsOpen(prev => !prev), [])

  const sendMessage = useCallback(() => {
    const nextMessage = inputValue.trim()

    if (!nextMessage || isLoading) return

    setMessages(prev => [...prev, createMessage('user', nextMessage)])
    setInputValue('')
    setIsLoading(true)

    responseTimeoutRef.current = window.setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          ...mockAssistantReply,
          id: `assistant-${Date.now()}`,
        },
      ])
      setIsLoading(false)
      responseTimeoutRef.current = null
    }, 650)
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

      if (responseTimeoutRef.current !== null) {
        window.clearTimeout(responseTimeoutRef.current)
      }
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
