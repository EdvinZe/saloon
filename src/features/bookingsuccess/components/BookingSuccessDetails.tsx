type Booking = {
  service: string
  duration: string
  date: string
  time: string
  barber: string
  deposit: string
}

interface Props {
  bookingId: string | null
  booking: Booking
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  padding: '10px 0',
}

export default function BookingSuccessDetails({ bookingId, booking }: Props) {
  const rows = [
    { label: 'Service', value: `${booking.service} · ${booking.duration}` },
    { label: 'Date & time', value: `${booking.date} · ${booking.time}` },
    { label: 'Barber', value: booking.barber },
    { label: 'Deposit paid', value: booking.deposit },
  ]

  return (
    <div style={{
      background: '#141008',
      border: '1px solid #2a2218',
      padding: '24px 28px',
      textAlign: 'left',
      marginBottom: '24px',
    }}>
      {bookingId && (
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
          Ref: {bookingId}
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
          }}>
            {row.value}
          </span>
        </div>
      ))}
    </div>
  )
}