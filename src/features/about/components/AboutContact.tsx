import { IconAddress, IconHours, IconInstagram, IconPhone } from './ContactIcons'

export default function AboutContact() {
  return (
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
