import { Link } from 'react-router-dom'

export default function Cta() {
  return (
    <section style={{ padding: '100px 48px', textAlign: 'center' }}>
      <div style={{ width: '1px', height: '48px', background: '#2a2218', margin: '0 auto 40px' }} />
      <h2 style={{ fontSize: '40px', color: '#e8e0d0', fontWeight: 400, marginBottom: '16px' }}>
        Ready for your<br />
        <em style={{ color: '#c9a84c', fontStyle: 'italic' }}>best cut yet?</em>
      </h2>
      <p style={{ fontSize: '13px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '2px', marginBottom: '48px', textTransform: 'uppercase' }}>
        Online booking · Confirmed in 5 min · Deposit at checkout
      </p>
      <Link to="/booking">
        <button style={{
          background: 'transparent',
          color: '#c9a84c',
          border: '1px solid #c9a84c',
          padding: '20px 64px',
          fontSize: '13px',
          letterSpacing: '5px',
          textTransform: 'uppercase',
          cursor: 'pointer',
          fontFamily: 'Georgia, serif',
          fontWeight: 400,
        }}>
          Get your appointment
        </button>
      </Link>
    </section>
  )
}
