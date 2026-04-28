export default function Footer() {
  return (
    <footer style={{
      padding: '28px 48px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderTop: '1px solid #2a2218',
    }}>
      <span style={{ fontSize: '11px', color: '#3a3020', fontFamily: 'sans-serif', letterSpacing: '2px' }}>
        © 2025 Saloon Barbershop · Vilnius
      </span>
      <span style={{ fontSize: '13px', letterSpacing: '6px', color: '#3a3020', textTransform: 'uppercase' }}>
        Saloon
      </span>
    </footer>
  )
}
