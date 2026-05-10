import type { HomeStat } from '../utils/homeStats'

interface Props {
  stats: HomeStat[]
}

export default function Stats({ stats }: Props) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
        borderBottom: '1px solid #2a2218',
        borderTop: '1px solid #2a2218',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {stats.map((s) => (
        <div
          key={s.label}
          style={{
            padding: 'clamp(22px, 6vw, 36px) 16px',
            textAlign: 'center',
            borderRight: '1px solid #2a2218',
            borderBottom: '1px solid #2a2218',
            minWidth: 0,
            boxSizing: 'border-box',
          }}
        >
          <div
            style={{
              fontSize: 'clamp(26px, 7vw, 38px)',
              color: '#c9a84c',
              fontWeight: 400,
              marginBottom: '6px',
            }}
          >
            {s.num}
          </div>

          <div
            style={{
              fontSize: '10px',
              color: '#5a5040',
              letterSpacing: '3px',
              textTransform: 'uppercase',
              fontFamily: 'sans-serif',
              overflowWrap: 'break-word',
            }}
          >
            {s.label}
          </div>
        </div>
      ))}
    </div>
  )
}