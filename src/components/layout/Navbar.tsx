import { Link } from 'react-router-dom'

const NAV_ITEMS: { label: string; to: string | null }[] = [
  { label: 'Services',  to: null },
  { label: 'Our team',  to: null },
  { label: 'Works',     to: '/works' },
  { label: 'About',     to: null },
  { label: 'Contact',   to: null },
]

const linkStyle: React.CSSProperties = {
  color: '#c0b090',
  fontSize: '11px',
  letterSpacing: '2px',
  textDecoration: 'none',
  textTransform: 'uppercase',
  fontFamily: 'sans-serif',
  padding: '6px 0',
  transition: 'color 0.2s',
}

export default function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '22px 48px',
      borderBottom: '1px solid #2a2218',
      background: '#0f0f0f',
    }}>
      <Link to="/" style={{
        fontSize: '20px',
        letterSpacing: '8px',
        color: '#c9a84c',
        fontWeight: 400,
        textTransform: 'uppercase',
        textDecoration: 'none',
        fontFamily: 'Georgia, serif',
      }}>
        Saloon
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: '40px', marginLeft: '80px' }}>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          {NAV_ITEMS.map(({ label, to }) =>
            to ? (
              <Link
                key={label}
                to={to}
                style={linkStyle}
                onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
                onMouseLeave={e => (e.currentTarget.style.color = '#c0b090')}
              >
                {label}
              </Link>
            ) : (
              <a
                key={label}
                href="#"
                style={linkStyle}
                onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
                onMouseLeave={e => (e.currentTarget.style.color = '#c0b090')}
              >
                {label}
              </a>
            )
          )}
        </div>

        <Link to="/booking">
          <button style={{
            background: 'transparent',
            border: '1px solid #c9a84c',
            color: '#c9a84c',
            padding: '11px 26px',
            fontSize: '11px',
            letterSpacing: '3px',
            textTransform: 'uppercase',
            cursor: 'pointer',
            fontFamily: 'Georgia, serif',
            fontWeight: 400,
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(201,168,76,0.08)'
            e.currentTarget.style.boxShadow = '0 0 20px rgba(201,168,76,0.2)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.boxShadow = 'none'
          }}
          >
            Book now
          </button>
        </Link>
      </div>
    </nav>
  )
}