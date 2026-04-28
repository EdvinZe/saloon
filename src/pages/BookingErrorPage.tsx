import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import Footer from '../components/layout/Footer'

interface ErrorConfig {
  title: string
  sub: string
  btn: string
  btnHref: string
}

// Keyed by `type` or `payment_failed.{reason}` for payment sub-types
const ERROR_MAP: Record<string, ErrorConfig> = {
  'payment_failed.card_declined': {
    title: 'Payment failed',
    sub: "We couldn't process your payment — your card was declined. Please try a different card or contact your bank.",
    btn: 'Try another card →',
    btnHref: '/booking',
  },
  'payment_failed.insufficient_funds': {
    title: 'Payment failed',
    sub: "We couldn't process your payment — insufficient funds on your card. Please try a different card.",
    btn: 'Try another card →',
    btnHref: '/booking',
  },
  session_expired: {
    title: 'Slot just taken',
    sub: 'Someone booked this time slot while you were checking out. Please go back and choose another time.',
    btn: 'Choose another time →',
    btnHref: '/booking',
  },
  stripe_error: {
    title: 'Something went wrong',
    sub: 'We had a technical issue on our end. Your card was not charged. Please try again.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
  booking_cancelled: {
    title: 'Booking cancelled',
    sub: 'Your booking was cancelled by the barber. Please choose another time or a different barber.',
    btn: 'Book again →',
    btnHref: '/booking',
  },
  default: {
    title: 'Something went wrong',
    sub: 'An unexpected error occurred. Your card was not charged. Please try again.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
}

export default function BookingErrorPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const type = params.get('type') ?? ''
  const reason = params.get('reason') ?? ''

  const key = type === 'payment_failed' ? `payment_failed.${reason}` : type
  const config = ERROR_MAP[key] ?? ERROR_MAP['default']

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px 24px',
        minHeight: 'calc(100vh - 70px)',
      }}>
        <div style={{ width: '100%', maxWidth: '480px', textAlign: 'center' }}>
          {/* Dark-red X circle */}
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            border: '1px solid #3a2020',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 32px',
            fontSize: '26px',
            color: '#8a4040',
            background: 'rgba(138,64,64,0.05)',
          }}>
            ✕
          </div>

          <h1 style={{ fontSize: '32px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif', marginBottom: '16px' }}>
            {config.title}
          </h1>
          <p style={{ fontSize: '14px', color: '#7a7060', fontFamily: 'sans-serif', lineHeight: 1.8, maxWidth: '400px', margin: '0 auto 40px' }}>
            {config.sub}
          </p>

          {/* Primary (gold) + Secondary (grey) buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate(config.btnHref)}
              style={{
                background: 'transparent',
                border: '1px solid #c9a84c',
                color: '#c9a84c',
                padding: '14px 28px',
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
              {config.btn}
            </button>

            <Link to="/" style={{ textDecoration: 'none' }}>
              <button
                style={{
                  background: 'transparent',
                  border: '1px solid #2a2218',
                  color: '#7a7060',
                  padding: '14px 28px',
                  fontSize: '11px',
                  letterSpacing: '3px',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                  fontFamily: 'Georgia, serif',
                  fontWeight: 400,
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = '#5a5040'
                  e.currentTarget.style.color = '#e8e0d0'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = '#2a2218'
                  e.currentTarget.style.color = '#7a7060'
                }}
              >
                ← Back to home
              </button>
            </Link>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  )
}
