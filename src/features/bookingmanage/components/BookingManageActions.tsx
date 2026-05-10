type ActivePanel = 'none' | 'reschedule' | 'cancel'

interface Props {
  activePanel: ActivePanel
  onSelect: (panel: 'reschedule' | 'cancel') => void
}

export default function BookingManageActions({ activePanel, onSelect }: Props) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '4px', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>

      {/* Reschedule */}
      <div
        onClick={() => onSelect('reschedule')}
        style={{
          background: activePanel === 'reschedule' ? 'rgba(201,168,76,0.05)' : '#141008',
          border: activePanel === 'reschedule' ? '1px solid #c9a84c' : '1px solid #2a2218',
          padding: '20px',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.2s',
          boxSizing: 'border-box',
          minWidth: 0,
        }}
        onMouseEnter={e => { if (activePanel !== 'reschedule') (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
        onMouseLeave={e => { if (activePanel !== 'reschedule') (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
      >
        <div style={{ fontSize: '22px', color: '#c9a84c', marginBottom: '8px' }}>↺</div>
        <div style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'Georgia, serif', marginBottom: '4px' }}>Reschedule</div>
        <div style={{ fontSize: '10px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
          Change date, time or service
        </div>
      </div>

      {/* Cancel */}
      <div
        onClick={() => onSelect('cancel')}
        style={{
          background: activePanel === 'cancel' ? 'rgba(200,112,112,0.05)' : '#141008',
          border: activePanel === 'cancel' ? '1px solid #c87070' : '1px solid #2a2218',
          padding: '20px',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.2s',
          boxSizing: 'border-box',
          minWidth: 0,
        }}
        onMouseEnter={e => { if (activePanel !== 'cancel') (e.currentTarget as HTMLDivElement).style.borderColor = '#c87070' }}
        onMouseLeave={e => { if (activePanel !== 'cancel') (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
      >
        <div style={{ fontSize: '22px', color: '#c87070', marginBottom: '8px' }}>✕</div>
        <div style={{ fontSize: '13px', color: '#c87070', fontFamily: 'Georgia, serif', marginBottom: '4px' }}>Cancel booking</div>
        <div style={{ fontSize: '10px', color: '#7a5050', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
          Deposit fully refunded
        </div>
      </div>
    </div>
  )
}
