import { format } from 'date-fns'
import type { BookingPaymentResult } from '../api'

type Booking = NonNullable<BookingPaymentResult['booking']>

interface Props {
  booking: Booking
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  gap: '12px',
  flexWrap: 'wrap',
  padding: '10px 0',
}

function formatDateTime(value: string) {
  return format(new Date(value), 'MMMM d, yyyy · HH:mm')
}

function formatDeposit(cents: number, currency: string) {
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency,
  }).format(cents / 100)
}

export default function BookingSuccessDetails({ booking }: Props) {
  const customerName = `${booking.customer_first_name} ${booking.customer_last_name}`
  const rows = [
    { label: 'Date & time', value: formatDateTime(booking.start_at) },
    { label: 'Customer', value: customerName },
    { label: 'Deposit paid', value: formatDeposit(booking.deposit_amount_cents, booking.currency) },
  ]

  return (
    <div style={{
      background: '#141008',
      border: '1px solid #2a2218',
      padding: '24px 28px',
      textAlign: 'left',
      marginBottom: '24px',
    }}>
      {booking.booking_code && (
        <div style={{
          fontSize: '10px',
          color: '#3a3020',
          fontFamily: 'sans-serif',
          letterSpacing: '2px',
          textTransform: 'uppercase',
          marginBottom: '16px',
          paddingBottom: '12px',
          borderBottom: '1px solid #1a1810',
        }}>
          Ref: {booking.booking_code}
        </div>
      )}

      {rows.map((row, i) => (
        <div
          key={row.label}
          style={{
            ...rowStyle,
            borderBottom: i === rows.length - 1 ? 'none' : '1px solid #1a1810',
          }}
        >
          <span style={{
            fontSize: '11px',
            color: '#5a5040',
            fontFamily: 'sans-serif',
            letterSpacing: '1px',
          }}>
            {row.label}
          </span>

          <span style={{
            fontSize: '13px',
            color: '#e8e0d0',
            fontFamily: 'sans-serif',
            textAlign: 'right',
            overflowWrap: 'anywhere',
          }}>
            {row.value}
          </span>
        </div>
      ))}
    </div>
  )
}
