import { useCallback, useEffect, useState } from 'react'
import { sendAIMessage } from '../api/aiAssistantApi'
import type { AIChatContextMessage, AIChatMessage, BookingIntentResponse } from '../types'

const unavailableMessage = 'AI assistant is temporarily unavailable. Please try again in a moment.'
const maxContextMessages = 8

function createMessage(
  role: AIChatMessage['role'],
  text: string,
  metadata?: BookingIntentResponse
): AIChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    text,
    createdAt: new Date().toISOString(),
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
      const response = await sendAIMessage(nextMessage, conversationContext)
      setMessages(prev => [
        ...prev,
        createMessage('assistant', response.assistant_message, response),
      ])
    } catch {
      setMessages(prev => [...prev, createMessage('assistant', unavailableMessage)])
    } finally {
      setIsLoading(false)
    }
  }, [inputValue, isLoading, messages])

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
