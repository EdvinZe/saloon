import { Link, useLocation, useNavigate } from 'react-router-dom'
import { NAV_ITEMS } from '../../shared/lib/navItems'
import { scrollToSection } from '../../shared/lib/scroll'

const linkStyle: React.CSSProperties = {
  color: '#3a3020',
  fontSize: '11px',
  letterSpacing: '2px',
  textDecoration: 'none',
  textTransform: 'uppercase',
  fontFamily: 'sans-serif',
  transition: 'color 0.2s',
}

export default function Footer() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <footer style={{
      padding: '28px 48px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderTop: '1px solid #2a2218',
    }}>
      <span style={{ fontSize: '11px', color: '#3a3020', fontFamily: 'sans-serif', letterSpacing: '2px' }}>
        © 2026 Saloon Barbershop · Vilnius
      </span>

      <div style={{ display: 'flex', gap: '28px', alignItems: 'center' }}>
        {NAV_ITEMS.map(item =>
          item.kind === 'section' ? (
            <a
              key={item.label}
              href={`#${item.sectionId}`}
              style={linkStyle}
              onClick={e => { e.preventDefault(); scrollToSection(item.sectionId, location.pathname, navigate) }}
              onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
              onMouseLeave={e => (e.currentTarget.style.color = '#3a3020')}
            >
              {item.label}
            </a>
          ) : (
            <Link
              key={item.label}
              to={item.to}
              style={linkStyle}
              onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
              onMouseLeave={e => (e.currentTarget.style.color = '#3a3020')}
            >
              {item.label}
            </Link>
          )
        )}
      </div>

      <span style={{ fontSize: '13px', letterSpacing: '6px', color: '#3a3020', textTransform: 'uppercase' }}>
        Saloon
      </span>
    </footer>
  )
}
