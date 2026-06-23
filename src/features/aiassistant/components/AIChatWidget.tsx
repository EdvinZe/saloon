import { useLocation, useNavigate } from 'react-router-dom'
import AIChatHeader from './AIChatHeader'
import AIChatInput from './AIChatInput'
import AIChatMessages from './AIChatMessages'
import { useAIChatWidget } from '../hooks/useAIChatWidget'
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
  } = useAIChatWidget()

  if (location.pathname.startsWith('/admin')) {
    return null
  }

  const handleBookManually = () => {
    navigate('/booking')
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
