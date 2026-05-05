export default function BookingSuccessHeader() {
  return (
    <>
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

      <h1 style={{
        fontSize: '32px',
        color: '#e8e0d0',
        fontWeight: 400,
        fontFamily: 'Georgia, serif',
        marginBottom: '10px',
      }}>
        Booking confirmed
      </h1>

      <p style={{
        fontSize: '10px',
        letterSpacing: '4px',
        textTransform: 'uppercase',
        color: '#7a7060',
        fontFamily: 'sans-serif',
        marginBottom: '36px',
      }}>
        See you soon
      </p>
    </>
  )
}