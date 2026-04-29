import Footer from '../components/layout/Footer'
import { MOCK_MASTERS } from '../shared/data/mockData'

export default function AboutPage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', color: '#e8e0d0' }}>

      {/* ── Hero ─────────────────────────────────────────────── */}
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

      {/* ── Story ────────────────────────────────────────────── */}
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

      {/* ── Team ─────────────────────────────────────────────── */}
      <section id="team" style={{ padding: '64px 48px' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <p style={{
            fontSize: '11px',
            letterSpacing: '5px',
            color: '#c9a84c',
            textTransform: 'uppercase',
            fontFamily: 'sans-serif',
            marginBottom: '16px',
          }}>
            The team
          </p>
          <h2 style={{
            fontSize: '36px',
            fontFamily: 'Georgia, serif',
            fontWeight: 400,
            color: '#e8e0d0',
          }}>
            Meet your barber
          </h2>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '1px',
          background: '#0f0f0f',
          justifyContent: 'center',
        }}>
          {MOCK_MASTERS.map(master => (
            <div key={master.id} style={{
              background: '#0f0f0f',
              width: 'calc(33.333% - 1px)',
              padding: '36px 28px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '14px',
            }}>
              <div style={{
                width: '72px',
                height: '72px',
                borderRadius: '50%',
                border: '1px solid #3a3020',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '15px',
                letterSpacing: '2px',
                color: '#c9a84c',
                fontFamily: 'Georgia, serif',
                marginBottom: '4px',
              }}>
                {master.initials}
              </div>

              <p style={{
                fontSize: '17px',
                fontFamily: 'Georgia, serif',
                fontWeight: 400,
                color: '#e8e0d0',
              }}>
                {master.name}
              </p>

              <p style={{
                fontSize: '10px',
                letterSpacing: '3px',
                textTransform: 'uppercase',
                color: '#c9a84c',
                fontFamily: 'sans-serif',
              }}>
                {master.role}
              </p>

              <p style={{
                fontSize: '12px',
                lineHeight: 1.7,
                color: '#5a5040',
                fontFamily: 'sans-serif',
                flexGrow: 1,
              }}>
                {master.bio}
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', justifyContent: 'center' }}>
                {master.tags.map(tag => (
                  <span key={tag} style={{
                    fontSize: '9px',
                    letterSpacing: '2px',
                    textTransform: 'uppercase',
                    color: '#5a5040',
                    fontFamily: 'sans-serif',
                    border: '1px solid #2a2218',
                    padding: '3px 8px',
                  }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Contact ──────────────────────────────────────────── */}
      <section id="contact" style={{ background: '#2a2218' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '1px',
        }}>
          {/* Left — contact info */}
          <div style={{ background: '#0f0f0f', padding: '48px' }}>
            <h2 style={{
              fontSize: '22px',
              fontFamily: 'Georgia, serif',
              fontWeight: 400,
              color: '#e8e0d0',
              marginBottom: '40px',
            }}>
              Find us
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <ContactRow
                icon={<IconAddress />}
                label="Address"
                value={<>Gedimino pr. 14<br />Vilnius LT-01103</>}
              />
              <ContactRow
                icon={<IconPhone />}
                label="Phone"
                value="+370 600 00000"
              />
              <ContactRow
                icon={<IconInstagram />}
                label="Instagram"
                value="@saloon.vilnius"
              />
              <ContactRow
                icon={<IconHours />}
                label="Hours"
                value={<>Mon–Fri &nbsp;10:00–20:00<br />Sat &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;10:00–18:00<br />Sun &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Closed</>}
              />
            </div>
          </div>

          {/* Right — map placeholder */}
          <div style={{
            background: '#141008',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '420px',
            gap: '14px',
          }}>
            <span style={{
              fontSize: '28px',
              color: '#c9a84c',
              lineHeight: 1,
              opacity: 0.5,
            }}>
              ◎
            </span>
            <p style={{
              fontSize: '10px',
              letterSpacing: '4px',
              textTransform: 'uppercase',
              color: '#3a3020',
              fontFamily: 'sans-serif',
            }}>
              Google Maps
            </p>
            <p style={{
              fontSize: '12px',
              color: '#3a3020',
              fontFamily: 'sans-serif',
              letterSpacing: '1px',
              textAlign: 'center',
            }}>
              Gedimino pr. 14<br />Vilnius LT-01103
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
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

function ContactRow({ icon, label, value }: {
  icon: React.ReactNode
  label: string
  value: React.ReactNode
}) {
  return (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
      <div style={{
        width: '36px',
        height: '36px',
        border: '1px solid #2a2218',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <p style={{
          fontSize: '10px',
          letterSpacing: '3px',
          textTransform: 'uppercase',
          color: '#5a5040',
          fontFamily: 'sans-serif',
          marginBottom: '4px',
        }}>
          {label}
        </p>
        <p style={{
          fontSize: '14px',
          lineHeight: 1.7,
          color: '#e8e0d0',
          fontFamily: 'sans-serif',
        }}>
          {value}
        </p>
      </div>
    </div>
  )
}

function IconAddress() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" strokeWidth="1.5">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
      <circle cx="12" cy="9" r="2" />
    </svg>
  )
}

function IconPhone() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" strokeWidth="1.5">
      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" />
    </svg>
  )
}

function IconInstagram() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" strokeWidth="1.5">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="0.5" fill="#c9a84c" />
    </svg>
  )
}

function IconHours() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" strokeWidth="1.5">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </svg>
  )
}
