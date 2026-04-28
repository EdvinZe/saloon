const STATS = [
  { num: '8+',   label: 'Years open' },
  { num: '4.9',  label: 'Google rating' },
  { num: '2 400',label: 'Happy clients' },
  { num: '100%', label: 'Satisfaction' },
]

export default function Stats() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', borderBottom: '1px solid #2a2218' }}>
      {STATS.map((s, i) => (
        <div key={i} style={{
          padding: '36px',
          textAlign: 'center',
          borderRight: i < 3 ? '1px solid #2a2218' : 'none',
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
