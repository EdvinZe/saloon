import { format } from 'date-fns'
import { useAvailableMasters } from '../hooks/useAvailableMasters'
import type { Master } from '../../../shared/data/mockData'

interface Props {
  date: string | null
  time: string | null
  selected: Master | null
  onSelect: (m: Master) => void
}

export default function MasterSelect({ date, time, selected, onSelect }: Props) {
  const { data: masters = [] } = useAvailableMasters(date, time)

  const formattedDate = date
    ? format(new Date(date + 'T12:00:00'), 'EEE, MMM d')
    : ''

  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
          Step 3
        </p>
        <h2 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400 }}>
          Available barbers on {formattedDate} at {time}
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1px', background: '#2a2218' }}>
        {masters.map(master => {
          const sel = selected?.id === master.id
          return (
            <div
              key={master.id}
              onClick={() => onSelect(master)}
              style={{
                background: sel ? 'rgba(201,168,76,0.06)' : '#141008',
                padding: '36px 28px',
                textAlign: 'center',
                cursor: 'pointer',
                outline: sel ? '1px solid #c9a84c' : '1px solid transparent',
                outlineOffset: '-1px',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.background = 'rgba(201,168,76,0.03)' }}
              onMouseLeave={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.background = '#141008' }}
            >
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                border: `1px solid ${sel ? '#c9a84c' : '#3a3020'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                color: '#c9a84c',
                fontFamily: 'sans-serif',
                margin: '0 auto 20px',
                transition: 'border-color 0.2s',
              }}>
                {master.initials}
              </div>
              <div style={{ fontSize: '18px', color: '#e8e0d0', marginBottom: '6px' }}>{master.name}</div>
              <div style={{ fontSize: '10px', color: '#c9a84c', letterSpacing: '3px', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px' }}>
                {master.role}
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
                {master.tags.map(tag => (
                  <span key={tag} style={{ fontSize: '10px', color: '#7a7060', fontFamily: 'sans-serif', border: '1px solid #2a2218', padding: '3px 8px' }}>
                    {tag}
                  </span>
                ))}
              </div>
              {sel && (
                <div style={{ marginTop: '16px', fontSize: '10px', letterSpacing: '3px', textTransform: 'uppercase', color: '#c9a84c', fontFamily: 'sans-serif' }}>
                  ✓ Selected
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
