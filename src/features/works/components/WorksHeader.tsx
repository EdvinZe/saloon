export default function WorksHeader() {
  return (
    <div style={{
      textAlign: 'center',
      padding: '72px 48px 56px',
      borderBottom: '1px solid #2a2218',
    }}>
      <p style={{
        color: '#c9a84c',
        fontSize: '11px',
        letterSpacing: '4px',
        textTransform: 'uppercase',
        fontFamily: 'sans-serif',
        marginBottom: '18px',
      }}>
        Portfolio
      </p>
      <h1 style={{
        color: '#e8e0d0',
        fontSize: '38px',
        fontFamily: 'Georgia, serif',
        fontWeight: 400,
        letterSpacing: '2px',
        marginBottom: '16px',
      }}>
        Our work
      </h1>
      <p style={{
        color: '#7a7060',
        fontSize: '14px',
        fontFamily: 'sans-serif',
        letterSpacing: '1px',
      }}>
        Every cut tells a story
      </p>
    </div>
  )
}