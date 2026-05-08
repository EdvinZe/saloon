export default function AboutHero() {
  return (
    <section style={{
      padding: '80px 48px 64px',
      textAlign: 'center',
      borderBottom: '1px solid #2a2218',
    }}>
      <p style={{
        fontSize: '11px',
        letterSpacing: '5px',
        color: '#c9a84c',
        textTransform: 'uppercase',
        fontFamily: 'sans-serif',
        marginBottom: '24px',
      }}>
        Our story
      </p>
      <h1 style={{
        fontSize: '44px',
        fontFamily: 'Georgia, serif',
        fontWeight: 400,
        lineHeight: 1.2,
        color: '#e8e0d0',
        marginBottom: '28px',
      }}>
        More than a cut.<br />
        <em style={{ color: '#c9a84c', fontStyle: 'italic' }}>A ritual.</em>
      </h1>
      <p style={{
        fontSize: '15px',
        lineHeight: 1.8,
        color: '#7a7060',
        fontFamily: 'sans-serif',
        maxWidth: '560px',
        margin: '0 auto',
      }}>
        Saloon is a barbershop built on the belief that the time a man spends in the chair
        should feel like his own. No rush. No noise. Just craft.
      </p>
    </section>
  )
}
