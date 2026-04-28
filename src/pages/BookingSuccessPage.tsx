import { useSearchParams, Link } from 'react-router-dom'
import Footer from '../components/layout/Footer'

// Mock data — swap for useQuery(getBooking(bookingId)) once API is ready
const MOCK_BOOKING = {
  service: 'Haircut',
  duration: '45 min',
  date: 'Tuesday, Apr 28',
  time: '09:30',
  barber: 'Alex Kravtsov',
  deposit: '€8',
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  padding: '10px 0',
  borderBottom: '1px solid #1a1810',
}

export default function BookingSuccessPage() {
  const [params] = useSearchParams()
  const bookingId = params.get('booking_id')
  const booking = MOCK_BOOKING

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
          {/* Gold checkmark circle */}
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            border: '1px solid #c9a84c',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 32px',
            fontSize: '26px',
            color: '#c9a84c',
            background: 'rgba(201,168,76,0.05)',
          }}>
            ✓
          </div>

          <h1 style={{ fontSize: '32px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif', marginBottom: '10px' }}>
            Booking confirmed
          </h1>
          <p style={{ fontSize: '10px', letterSpacing: '4px', textTransform: 'uppercase', color: '#7a7060', fontFamily: 'sans-serif', marginBottom: '36px' }}>
            See you soon
          </p>

          {/* Details card */}
          <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px 28px', textAlign: 'left', marginBottom: '24px' }}>
            {bookingId && (
              <div style={{ fontSize: '10px', color: '#3a3020', fontFamily: 'sans-serif', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid #1a1810' }}>
                Ref: {bookingId}
              </div>
            )}
            {([
              { label: 'Service',      value: `${booking.service} · ${booking.duration}` },
              { label: 'Date & time',  value: `${booking.date} · ${booking.time}` },
              { label: 'Barber',       value: booking.barber },
              { label: 'Deposit paid', value: booking.deposit },
            ] as { label: string; value: string }[]).map((row, i, arr) => (
              <div key={row.label} style={{ ...rowStyle, borderBottom: i === arr.length - 1 ? 'none' : '1px solid #1a1810' }}>
                <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>{row.label}</span>
                <span style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'sans-serif' }}>{row.value}</span>
              </div>
            ))}
          </div>

          <p style={{ fontSize: '12px', color: '#5a5040', fontFamily: 'sans-serif', lineHeight: 1.8, marginBottom: '36px' }}>
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
        </div>
      </div>
      <Footer />
    </div>
  )
}
