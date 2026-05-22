import { useAboutMasters } from '../hooks/useAboutMasters'

export default function AboutTeam() {
  const { data: masters = [] } = useAboutMasters()

  return (
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
        {masters.map(master => (
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
              {master.services.map(service => (
                <span key={service.id} style={{
                  fontSize: '9px',
                  letterSpacing: '2px',
                  textTransform: 'uppercase',
                  color: '#5a5040',
                  fontFamily: 'sans-serif',
                  border: '1px solid #2a2218',
                  padding: '3px 8px',
                }}>
                  {service.name}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
