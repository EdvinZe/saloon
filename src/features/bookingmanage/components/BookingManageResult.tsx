type DoneType = 'rescheduled' | 'cancelled'

interface Props {
  doneType: DoneType
  depositPaid: number
}

export default function BookingManageResult({ doneType, depositPaid }: Props) {
  const cancelled = doneType === 'cancelled'

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '80px clamp(16px, 5vw, 24px)', minHeight: 'calc(100vh - 70px)',
      width: '100%', boxSizing: 'border-box',
    }}>
      <div style={{ width: '100%', maxWidth: '520px', textAlign: 'center', minWidth: 0 }}>
        <div style={{
          width: '72px', height: '72px', borderRadius: '50%',
          border: `1px solid ${cancelled ? '#c87070' : '#c9a84c'}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 32px', fontSize: '26px',
          color: cancelled ? '#c87070' : '#c9a84c',
          background: cancelled ? 'rgba(200,112,112,0.05)' : 'rgba(201,168,76,0.05)',
        }}>
          {cancelled ? '✕' : '✓'}
        </div>
        <h1 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif', marginBottom: '10px' }}>
          {cancelled ? 'Booking cancelled' : 'Booking rescheduled'}
        </h1>
        <p style={{ fontSize: '12px', color: '#7a7060', fontFamily: 'sans-serif', lineHeight: 1.8 }}>
          {cancelled
            ? `Your deposit of €${depositPaid} will be refunded within 3–5 business days.`
            : 'Your appointment has been updated. A confirmation will be sent shortly.'}
        </p>
      </div>
    </div>
  )
}
