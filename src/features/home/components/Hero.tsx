import { Link } from 'react-router-dom'

export default function Hero() {
  return (
    <section style={{
      padding: 'clamp(72px, 12vw, 100px) clamp(20px, 6vw, 48px) clamp(56px, 10vw, 80px)',
      textAlign: 'center',
      borderBottom: '1px solid #2a2218',
    }}>
      <p style={{
        fontSize: '10px',
        letterSpacing: '5px',
        color: '#c9a84c',
        textTransform: 'uppercase',
        fontFamily: 'sans-serif',
        marginBottom: '28px',
        opacity: 0.8,
      }}>
        Premium Barbershop · Vilnius, Lithuania
      </p>

      <h1 style={{
        fontSize: 'clamp(40px, 9vw, 62px)',
        lineHeight: 1.1,
        color: '#e8e0d0',
        fontWeight: 400,
        marginBottom: '28px',
        fontFamily: 'Georgia, serif',
      }}>
        Where every cut<br />
        tells a <em style={{ color: '#c9a84c', fontStyle: 'italic' }}>story</em>
      </h1>

      <p style={{
        fontSize: '15px',
        lineHeight: 1.9,
        color: '#7a7060',
        fontFamily: 'sans-serif',
        maxWidth: '480px',
        margin: '0 auto 52px',
      }}>
        Expert barbers, timeless techniques, modern results.
        Book your seat online in under 2 minutes.
      </p>

      <Link to="/booking">
        <button style={{
          background: 'transparent',
          color: '#c9a84c',
          border: '1px solid #c9a84c',
          padding: '18px clamp(28px, 12vw, 64px)',
          fontSize: '13px',
          letterSpacing: 'clamp(3px, 1vw, 5px)',
          textTransform: 'uppercase',
          cursor: 'pointer',
          fontFamily: 'Georgia, serif',
          fontWeight: 400,
          transition: 'all 0.2s',
          maxWidth: '100%',
          boxSizing: 'border-box',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'rgba(201,168,76,0.08)'
          e.currentTarget.style.boxShadow = '0 0 32px rgba(201,168,76,0.25)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.boxShadow = 'none'
        }}
        >
          Reserve your seat
        </button>
      </Link>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        margin: '64px auto 0',
        maxWidth: '400px',
        width: '100%',
      }}>
        <div style={{ flex: 1, height: '1px', background: '#2a2218' }} />
        <span style={{
          fontSize: '10px',
          letterSpacing: '3px',
          color: '#4a4030',
          fontFamily: 'sans-serif',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}>
          Est. 2016 · Vilnius
        </span>
        <div style={{ flex: 1, height: '1px', background: '#2a2218' }} />
      </div>
    </section>
  )
}
