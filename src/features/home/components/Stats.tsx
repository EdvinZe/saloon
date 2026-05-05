import type { HomeStat } from '../utils/homeStats'

interface Props {
  stats: HomeStat[]
}

export default function Stats({ stats }: Props) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${stats.length}, 1fr)`, borderBottom: '1px solid #2a2218' }}>
      {stats.map((s, i) => (
        <div key={s.label} style={{
          padding: '36px',
          textAlign: 'center',
          borderRight: i < stats.length - 1 ? '1px solid #2a2218' : 'none',
        }}>
          <div style={{ fontSize: '38px', color: '#c9a84c', fontWeight: 400, marginBottom: '6px' }}>
            {s.num}
          </div>
          <div style={{ fontSize: '10px', color: '#5a5040', letterSpacing: '3px', textTransform: 'uppercase', fontFamily: 'sans-serif' }}>
            {s.label}
          </div>
        </div>
      ))}
    </div>
  )
}