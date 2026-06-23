interface AIChatHeaderProps {
  isOpen: boolean
  onToggle: () => void
}

export default function AIChatHeader({ isOpen, onToggle }: AIChatHeaderProps) {
  return (
    <button
      type="button"
      className="ai-chat-header"
      aria-label={isOpen ? 'Collapse booking assistant' : 'Open booking assistant'}
      aria-expanded={isOpen}
      onClick={onToggle}
    >
      <span className="ai-chat-header-icon" aria-hidden="true">
        ✦
      </span>
      <span className="ai-chat-title-wrap">
        <span className="ai-chat-title">Booking Assistant</span>
        <span className="ai-chat-status">
          <span className="ai-chat-status-dot" aria-hidden="true" />
          Online
        </span>
      </span>
      <span className={`ai-chat-toggle ${isOpen ? 'ai-chat-toggle-open' : ''}`} aria-hidden="true">
        ▾
      </span>
    </button>
  )
}
