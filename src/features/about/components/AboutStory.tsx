export default function AboutStory() {
  return (
    <section style={{ background: '#2a2218' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1px',
      }}>
        <StoryColumn
          eyebrow="How it started"
          title="Built on craft, not compromise"
        >
          Saloon opened in 2018 in a narrow building on Gedimino with a single chair, two mirrors,
          and a conviction that Vilnius deserved a place where a haircut was an event, not an errand.
          The founder, Alex Kravtsov, had spent a decade in London and St. Petersburg refining a
          simple idea: slow down, pay attention, do less better.
          <br /><br />
          The name was chosen deliberately — not salon, not studio. Saloon. A place with history,
          with warmth, with a door that stays open.
        </StoryColumn>

        <StoryColumn
          eyebrow="Where we are now"
          title="Three chairs, one standard"
        >
          Five barbers. One address. The same chair Alex sat in when he drew the first layout on a
          napkin is still in use. We have grown carefully — each master chosen not just for their
          skill but for how they treat the hour they share with a client.
          <br /><br />
          We don't rush appointments, we don't run loyalty schemes, and we don't have background
          music louder than conversation. We just cut hair — very well.
        </StoryColumn>
      </div>
    </section>
  )
}

function StoryColumn({ eyebrow, title, children }: {
  eyebrow: string
  title: string
  children: React.ReactNode
}) {
  return (
    <div style={{ background: '#0f0f0f', padding: '48px' }}>
      <div style={{ width: '32px', height: '1px', background: '#c9a84c', marginBottom: '28px' }} />
      <p style={{
        fontSize: '10px',
        letterSpacing: '4px',
        color: '#c9a84c',
        textTransform: 'uppercase',
        fontFamily: 'sans-serif',
        marginBottom: '16px',
      }}>
        {eyebrow}
      </p>
      <h3 style={{
        fontSize: '22px',
        fontFamily: 'Georgia, serif',
        fontWeight: 400,
        color: '#e8e0d0',
        marginBottom: '24px',
        lineHeight: 1.3,
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '14px',
        lineHeight: 1.9,
        color: '#7a7060',
        fontFamily: 'sans-serif',
      }}>
        {children}
      </p>
    </div>
  )
}
