interface GoldButtonProps {
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  style?: React.CSSProperties
  type?: 'button' | 'submit' | 'reset'
}

export default function GoldButton({ children, onClick, disabled, style, type = 'button' }: GoldButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={style}
      className="btn-gold py-3.5 px-7 text-[11px]"
    >
      {children}
    </button>
  )
}
