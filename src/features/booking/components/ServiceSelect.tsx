import { SERVICES } from '../../../shared/data/mockData'
import type { Service } from '../../../shared/data/mockData'
import Carousel from '../../../components/ui/Carousel'

interface Props {
  selected: Service | null
  onSelect: (s: Service) => void
}

export default function ServiceSelect({ selected, onSelect }: Props) {
  return (
    <div>
      <div style={{ marginBottom: '28px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
          Step 1
        </p>
        <h2 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400 }}>
          Choose your service
        </h2>
      </div>

      <Carousel visible={3}>
        {SERVICES.map(svc => {
          const sel = selected?.id === svc.id

          return (
            <div
              key={svc.id}
              onClick={() => onSelect(svc)}
              style={{
                background: sel ? 'rgba(201,168,76,0.06)' : '#141008',
                padding: '36px 28px',
                cursor: 'pointer',
                outline: sel ? '1px solid #c9a84c' : '1px solid #2a2218',
                outlineOffset: '-1px',
                transition: 'all 0.2s',
                height: '100%',
              }}
              onMouseEnter={e => {
                if (!sel) {
                  ;(e.currentTarget as HTMLDivElement).style.background = 'rgba(201,168,76,0.03)'
                }
              }}
              onMouseLeave={e => {
                if (!sel) {
                  ;(e.currentTarget as HTMLDivElement).style.background = '#141008'
                }
              }}
            >
              <div style={{
                width: '32px',
                height: '1px',
                background: sel ? '#c9a84c' : '#3a3020',
                marginBottom: '24px',
                transition: 'background 0.2s',
              }} />

              <div style={{
                fontSize: '20px',
                color: '#e8e0d0',
                marginBottom: '10px',
              }}>
                {svc.name}
              </div>

              <div style={{
                fontSize: '13px',
                color: '#5a5040',
                fontFamily: 'sans-serif',
                lineHeight: 1.8,
                marginBottom: '24px',
              }}>
                {svc.desc}
              </div>

              <div style={{
                fontSize: '22px',
                color: '#c9a84c',
                fontFamily: 'sans-serif',
              }}>
                {svc.price}
              </div>

              <div style={{
                fontSize: '10px',
                color: '#3a3020',
                fontFamily: 'sans-serif',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginTop: '4px',
              }}>
                {svc.dur}
              </div>

              {sel && (
                <div style={{
                  marginTop: '20px',
                  fontSize: '10px',
                  letterSpacing: '3px',
                  textTransform: 'uppercase',
                  color: '#c9a84c',
                  fontFamily: 'sans-serif',
                }}>
                  ✓ Selected
                </div>
              )}
            </div>
          )
        })}
      </Carousel>
    </div>
  )
}