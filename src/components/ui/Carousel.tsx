import { Children, useState, type ReactNode } from 'react'

interface Props {
  children: ReactNode
  visible?: number
}

export default function Carousel({ children, visible = 3 }: Props) {
  const items = Children.toArray(children)

  const [current, setCurrent] = useState(0)

  if (items.length === 0) {
    return null
  }

  const pages = Math.max(1, items.length - visible + 1)

  const go = (index: number) => {
    setCurrent(Math.max(0, Math.min(index, pages - 1)))
  }

  const canPrev = current > 0
  const canNext = current < pages - 1

  const offset = current * (100 / visible)

  return (
    <div style={{ position: 'relative' }}>
      {pages > 1 && (
        <button
          onClick={() => go(current - 1)}
          disabled={!canPrev}
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
            cursor: !canPrev ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            zIndex: 2,
            opacity: !canPrev ? 0.3 : 1,
            transition: 'all 0.2s',
          }}
        >
          ←
        </button>
      )}

      <div style={{ overflow: 'hidden' }}>
        <div
          style={{
            display: 'flex',
            gap: '1px',
            transition: 'transform 0.4s ease',
            transform: `translateX(-${offset}%)`,
          }}
        >
          {items.map((item, index) => (
            <div
              key={index}
              style={{
                flex: `0 0 calc(${100 / visible}% - 1px)`,
                minWidth: 0,
              }}
            >
              {item}
            </div>
          ))}
        </div>
      </div>

      {pages > 1 && (
        <button
          onClick={() => go(current + 1)}
          disabled={!canNext}
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
            cursor: !canNext ? 'not-allowed' : 'pointer',
            fontSize: '18px',
            zIndex: 2,
            opacity: !canNext ? 0.3 : 1,
            transition: 'all 0.2s',
          }}
        >
          →
        </button>
      )}

      {pages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '28px' }}>
          {Array.from({ length: pages }).map((_, index) => (
            <div
              key={index}
              onClick={() => go(index)}
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: index === current ? '#c9a84c' : '#2a2218',
                cursor: 'pointer',
                transition: 'background 0.2s',
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}