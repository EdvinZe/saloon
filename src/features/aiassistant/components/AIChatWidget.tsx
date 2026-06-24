import { useLocation, useNavigate } from 'react-router-dom'
import AIChatHeader from './AIChatHeader'
import AIChatInput from './AIChatInput'
import AIChatMessages from './AIChatMessages'
import { useAIChatWidget } from '../hooks/useAIChatWidget'
import type { BookingAssistantAction } from '../types'
import '../aiAssistant.css'

export default function AIChatWidget() {
  const location = useLocation()
  const navigate = useNavigate()
  const {
    isOpen,
    messages,
    inputValue,
    isLoading,
    setInputValue,
    closeWidget,
    toggleWidget,
    sendMessage,
    sendMessageText,
    resetDraft,
  } = useAIChatWidget()

  if (location.pathname.startsWith('/admin')) {
    return null
  }

  const handleBookManually = () => {
    navigate('/booking')
    closeWidget()
  }

  const handleAssistantAction = (action: BookingAssistantAction) => {
    if (action.type === 'open_booking_form') {
      navigate('/booking')
      closeWidget()
      return
    }

    if (action.type === 'send_message' && action.payload.message) {
      void sendMessageText(action.payload.message)
      return
    }

    if (action.type === 'reset_ai_draft') {
      resetDraft()
      return
    }

    if (
      action.type !== 'prefill_booking' ||
      action.payload.service_id == null ||
      action.payload.master_id == null ||
      !action.payload.date ||
      !action.payload.time
    ) return

    const params = new URLSearchParams({
      serviceId: String(action.payload.service_id),
      masterId: String(action.payload.master_id),
      date: action.payload.date,
      time: action.payload.time,
    })

    navigate(`/booking?${params.toString()}`)
    closeWidget()
  }

  return (
    <aside className={`ai-chat-widget ${isOpen ? 'ai-chat-widget-open' : 'ai-chat-widget-closed'}`} aria-label="Booking assistant chat">
      <AIChatHeader isOpen={isOpen} onToggle={toggleWidget} />

      <div className="ai-chat-panel" aria-hidden={!isOpen} inert={!isOpen}>
        <AIChatMessages
          messages={messages}
          isLoading={isLoading}
          onBookManually={handleBookManually}
          onAssistantAction={handleAssistantAction}
        />
        <AIChatInput
          inputValue={inputValue}
          isLoading={isLoading}
          onInputChange={setInputValue}
          onSend={sendMessage}
        />
      </div>
    </aside>
  )
}
