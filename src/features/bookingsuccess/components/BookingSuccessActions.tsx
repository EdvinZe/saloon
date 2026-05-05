import { Link } from 'react-router-dom'

export default function BookingSuccessActions() {
  return (
    <>
      <p style={{
        fontSize: '12px',
        color: '#5a5040',
        fontFamily: 'sans-serif',
        lineHeight: 1.8,
        marginBottom: '36px',
      }}>
        A confirmation has been sent. Your barber will be notified shortly.
      </p>

      <Link to="/" style={{ textDecoration: 'none' }}>
        <button
          style={{
            background: 'transparent',
            border: '1px solid #c9a84c',
            color: '#c9a84c',
            padding: '14px 36px',
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
          ← Back to home
        </button>
      </Link>
    </>
  )
}