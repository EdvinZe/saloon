import { useState } from 'react'

interface Master {
  id: string
  name: string
  role: string
  initials: string
  tags: string[]
}

interface MastersCarouselProps {
  masters: Master[]
}

const VISIBLE = 3

export default function MastersCarousel({ masters }: MastersCarouselProps) {
  const [current, setCurrent] = useState(0)
  const pages = Math.max(0, masters.length - VISIBLE + 1)

  const go = (n: number) => setCurrent(Math.max(0, Math.min(n, pages - 1)))

  const offset = current * (100 / VISIBLE)

  return (
    <section style={{ padding: '80px 48px', borderBottom: '1px solid #2a2218' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <p style={{
          fontSize: '10px',
          letterSpacing: '5px',
          color: '#c9a84c',
          textTransform: 'uppercase',
          fontFamily: 'sans-serif',
          marginBottom: '16px',
        }}>
          The team
        </p>
        <h2 style={{ fontSize: '34px', color: '#e8e0d0', fontWeight: 400 }}>
          Meet your barber
        </h2>
      </div>

      <div style={{ position: 'relative' }}>
        {/* Prev button */}
        <button
          onClick={() => go(current - 1)}
          disabled={current === 0}
          style={{
            position: 'absolute',
            top: '50%',
            left: '-22px',
            transform: 'translateY(-50%)',
            background: 'transparent',
            border: '1px solid #c9a84c',
            color: '#c9a84c',
            width: '44px',
            height: '44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: current === 0 ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            zIndex: 2,
            opacity: current === 0 ? 0.3 : 1,
            transition: 'all 0.2s',
          }}
        >
          ←
        </button>

        {/* Track */}
        <div style={{ overflow: 'hidden' }}>
          <div style={{
            display: 'flex',
            gap: '1px',
            transition: 'transform 0.4s ease',
            transform: `translateX(-${offset}%)`,
          }}>
            {masters.map(master => (
              <div key={master.id} style={{
                background: '#141008',
                padding: '40px 32px',
                textAlign: 'center',
                flex: `0 0 calc(${100 / VISIBLE}% - 1px)`,
                minWidth: 0,
              }}>
                <div style={{
                  width: '72px',
                  height: '72px',
                  borderRadius: '50%',
                  border: '1px solid #3a3020',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '22px',
                  color: '#c9a84c',
                  fontFamily: 'sans-serif',
                  margin: '0 auto 24px',
                }}>
                  {master.initials}
                </div>
                <div style={{ fontSize: '18px', color: '#e8e0d0', marginBottom: '6px' }}>
                  {master.name}
                </div>
                <div style={{
                  fontSize: '10px',
                  color: '#c9a84c',
                  letterSpacing: '3px',
                  textTransform: 'uppercase',
                  fontFamily: 'sans-serif',
                  marginBottom: '16px',
                }}>
                  {master.role}
                </div>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
                  {master.tags.map(tag => (
                    <span key={tag} style={{
                      fontSize: '10px',
                      color: '#7a7060',
                      fontFamily: 'sans-serif',
                      border: '1px solid #2a2218',
                      padding: '4px 10px',
                    }}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Next button */}
        <button
          onClick={() => go(current + 1)}
          disabled={current >= pages - 1}
          style={{
            position: 'absolute',
            top: '50%',
            right: '-22px',
            transform: 'translateY(-50%)',
            background: 'transparent',
            border: '1px solid #c9a84c',
            color: '#c9a84c',
            width: '44px',
            height: '44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: current >= pages - 1 ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            zIndex: 2,
            opacity: current >= pages - 1 ? 0.3 : 1,
            transition: 'all 0.2s',
          }}
        >
          →
        </button>
      </div>

      {/* Dots */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '28px' }}>
        {Array.from({ length: pages }).map((_, i) => (
          <div
            key={i}
            onClick={() => go(i)}
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: i === current ? '#c9a84c' : '#2a2218',
              cursor: 'pointer',
              transition: 'background 0.2s',
            }}
          />
        ))}
      </div>
    </section>
  )
}