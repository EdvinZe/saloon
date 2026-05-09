import type { Service } from '../../../shared/data/mockData'
import { SERVICES } from '../../../shared/data/mockData'
import { useBookingConfig } from '../../bookingconfig/hooks/useBookingConfig'

interface Props {
  selected: Service | null
  onSelect: (s: Service) => void
}

export default function ManageServiceSelect({ selected, onSelect }: Props) {
  const { data: bookingConfig } = useBookingConfig()
  const depositAmount = bookingConfig?.depositAmount ?? 10
  const currency = bookingConfig?.currency ?? 'EUR'
  const currencySymbol = currency === 'EUR' ? '€' : currency

  return (
    <div>
      <p style={{
        fontSize: '10px', letterSpacing: '3px', color: '#c9a84c',
        textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px',
      }}>
        Step 1 — Service
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1px', background: '#2a2218' }}>
        {SERVICES.map(svc => {
          const sel = selected?.id === svc.id
          return (
            <div
              key={svc.id}
              onClick={() => onSelect(svc)}
              style={{
                background: sel ? 'rgba(201,168,76,0.06)' : '#141008',
                padding: '20px 14px',
                cursor: 'pointer',
                outline: sel ? '1px solid #c9a84c' : '1px solid transparent',
                outlineOffset: '-1px',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.background = 'rgba(201,168,76,0.03)' }}
              onMouseLeave={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.background = '#141008' }}
            >
              <div style={{ fontSize: '15px', color: '#e8e0d0', marginBottom: '6px', fontFamily: 'Georgia, serif' }}>
                {svc.name}
              </div>
              <div style={{ fontSize: '12px', color: '#c9a84c', fontFamily: 'sans-serif', marginBottom: '4px' }}>
                dep. {currencySymbol}{depositAmount}
              </div>
              <div style={{ fontSize: '10px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
                {svc.dur}
              </div>
              {sel && (
                <div style={{ marginTop: '10px', fontSize: '9px', letterSpacing: '2px', textTransform: 'uppercase', color: '#c9a84c', fontFamily: 'sans-serif' }}>
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
