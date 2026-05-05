interface Props {
  children: React.ReactNode
  maxWidth?: string
  centeredText?: boolean
}

export default function CenteredPageLayout({
  children,
  maxWidth = '520px',
  centeredText = false,
}: Props) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '80px 24px',
      minHeight: 'calc(100vh - 70px)',
    }}>
      <div style={{
        width: '100%',
        maxWidth,
        textAlign: centeredText ? 'center' : 'left',
      }}>
        {children}
      </div>
    </div>
  )
}