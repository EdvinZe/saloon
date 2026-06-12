import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { NAV_ITEMS } from '../../shared/lib/navItems'
import { scrollToSection } from '../../shared/lib/scroll'

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
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <>
      <style>{`
        .navbar-desktop { display: flex; }
        .navbar-mobile-button { display: none; }
        .navbar-mobile-menu { display: none; }

        @media (max-width: 899px) {
          .navbar-root { padding: 18px 20px !important; }
          .navbar-desktop { display: none !important; }
          .navbar-mobile-button { display: block !important; }
          .navbar-mobile-menu { display: flex !important; }
        }
      `}</style>

      <nav
        className="navbar-root"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '22px 48px',
          borderBottom: '1px solid #2a2218',
          background: '#0f0f0f',
          width: '100%',
          boxSizing: 'border-box',
        }}
      >
        <Link to="/" style={{
          fontSize: '20px',
          letterSpacing: 'clamp(5px, 1.7vw, 8px)',
          color: '#c9a84c',
          fontWeight: 400,
          textTransform: 'uppercase',
          textDecoration: 'none',
          fontFamily: 'Georgia, serif',
        }}>
          Saloon
        </Link>

        <div className="navbar-desktop" style={{ alignItems: 'center', gap: 'clamp(24px, 4vw, 40px)', marginLeft: 'clamp(32px, 6vw, 80px)' }}>
          <div style={{ display: 'flex', gap: 'clamp(20px, 3vw, 32px)', alignItems: 'center' }}>
            {NAV_ITEMS.map(item =>
              item.kind === 'section' ? (
                <a
                  key={item.label}
                  href={`#${item.sectionId}`}
                  style={linkStyle}
                  onClick={e => { e.preventDefault(); scrollToSection(item.sectionId, location.pathname, navigate) }}
                  onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
                  onMouseLeave={e => (e.currentTarget.style.color = '#c0b090')}
                >
                  {item.label}
                </a>
              ) : (
                <Link
                  key={item.label}
                  to={item.to}
                  style={linkStyle}
                  onMouseEnter={e => (e.currentTarget.style.color = '#c9a84c')}
                  onMouseLeave={e => (e.currentTarget.style.color = '#c0b090')}
                >
                  {item.label}
                </Link>
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

        <button
          className="navbar-mobile-button"
          aria-label="Toggle navigation menu"
          aria-expanded={open}
          onClick={() => setOpen(prev => !prev)}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#c9a84c',
            fontSize: '24px',
            lineHeight: 1,
            cursor: 'pointer',
            padding: '4px 0 4px 12px',
          }}
        >
          ☰
        </button>
      </nav>

      {open && (
        <div
          className="navbar-mobile-menu"
          style={{
            flexDirection: 'column',
            gap: '14px',
            padding: '18px 20px 22px',
            borderBottom: '1px solid #2a2218',
            background: '#0f0f0f',
            width: '100%',
            boxSizing: 'border-box',
          }}
        >
          {NAV_ITEMS.map(item =>
            item.kind === 'section' ? (
              <a
                key={item.label}
                href={`#${item.sectionId}`}
                style={linkStyle}
                onClick={e => {
                  e.preventDefault()
                  setOpen(false)
                  scrollToSection(item.sectionId, location.pathname, navigate)
                }}
              >
                {item.label}
              </a>
            ) : (
              <Link
                key={item.label}
                to={item.to}
                style={linkStyle}
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            )
          )}

          <Link to="/booking" onClick={() => setOpen(false)} style={{ textDecoration: 'none' }}>
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
              width: '100%',
              boxSizing: 'border-box',
              transition: 'all 0.2s',
            }}>
              Book now
            </button>
          </Link>
        </div>
      )}
    </>
  )
}
