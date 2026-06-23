import type { FormEvent } from 'react'

interface AIChatInputProps {
  inputValue: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onSend: () => void
}

export default function AIChatInput({
  inputValue,
  isLoading,
  onInputChange,
  onSend,
}: AIChatInputProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    onSend()
  }

  return (
    <form className="ai-chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="ai-chat-input"
        value={inputValue}
        onChange={event => onInputChange(event.target.value)}
        placeholder="Type your message..."
        aria-label="Type your message to the booking assistant"
      />
      <button
        type="submit"
        className="ai-chat-send"
        aria-label="Send message"
        disabled={isLoading || inputValue.trim().length === 0}
      >
        <svg aria-hidden="true" width="17" height="17" viewBox="0 0 24 24" fill="none">
          <path d="M4 12L20 4L16 20L12 13L4 12Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
        </svg>
      </button>
    </form>
  )
}
