interface Props {
  depositPaid: number
  depositStatus: string
  onConfirm: () => void
  onKeep: () => void
  submitting: boolean
}

export default function CancelConfirm({ depositPaid, depositStatus, onConfirm, onKeep, submitting }: Props) {
  const willRefundDeposit = depositStatus === 'paid'

  return (
    <div>
      {/* Red warning box */}
      <div style={{
        border: '1px solid #5a2020',
        background: '#140808',
        padding: '20px 24px',
        marginBottom: '20px',
        boxSizing: 'border-box',
      }}>
        <div style={{ fontSize: '15px', color: '#c87070', fontFamily: 'Georgia, serif', marginBottom: '10px' }}>
          Cancel your booking?
        </div>
        <div style={{ fontSize: '12px', color: '#7a6060', fontFamily: 'sans-serif', lineHeight: 1.7 }}>
          Are you sure you want to cancel this booking?
          {willRefundDeposit && (
            <>
              {' '}Your deposit of <span style={{ color: '#c87070' }}>€{depositPaid}</span>
              {' '}will be refunded to the original payment method.
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {/* Confirm cancel — red */}
        <button
          onClick={onConfirm}
          disabled={submitting}
          style={{
            flex: 1,
            minWidth: '180px',
            padding: '13px',
            background: 'transparent',
            border: '1px solid #c87070',
            color: '#c87070',
            fontSize: '11px',
            letterSpacing: '2px',
            textTransform: 'uppercase',
            fontFamily: 'Georgia, serif',
            cursor: submitting ? 'not-allowed' : 'pointer',
            opacity: submitting ? 0.5 : 1,
            transition: 'all 0.2s',
            boxSizing: 'border-box',
          }}
          onMouseEnter={e => { if (!submitting) e.currentTarget.style.background = 'rgba(200,112,112,0.08)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
        >
          {submitting ? 'Cancelling...' : 'Yes, cancel booking'}
        </button>

        {/* Keep booking — grey */}
        <button
          onClick={onKeep}
          disabled={submitting}
          style={{
            flex: 1,
            minWidth: '180px',
            padding: '13px',
            background: 'transparent',
            border: '1px solid #3a3020',
            color: '#7a7060',
            fontSize: '11px',
            letterSpacing: '2px',
            textTransform: 'uppercase',
            fontFamily: 'Georgia, serif',
            cursor: submitting ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            boxSizing: 'border-box',
          }}
          onMouseEnter={e => { if (!submitting) e.currentTarget.style.borderColor = '#5a5040' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = '#3a3020' }}
        >
          Keep my booking
        </button>
      </div>
    </div>
  )
}
