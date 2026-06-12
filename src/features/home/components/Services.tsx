import type { Service } from '../../services/api'
import Carousel from '../../../components/ui/Carousel'

interface Props {
  services: Service[]
}

export default function Services({ services }: Props) {
  return (
    <section style={{ padding: '80px 48px', borderBottom: '1px solid #2a2218', background: '#0a0a08' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <p style={{
          fontSize: '10px',
          letterSpacing: '5px',
          color: '#c9a84c',
          textTransform: 'uppercase',
          fontFamily: 'sans-serif',
          marginBottom: '16px',
        }}>
          What we offer
        </p>

        <h2 style={{ fontSize: '34px', color: '#e8e0d0', fontWeight: 400 }}>
          Our services
        </h2>
      </div>

      {services.length === 0 ? (
        <div style={{ maxWidth: '560px', margin: '0 auto', border: '1px solid #2a2218', background: '#0f0f0f', padding: '28px 24px', textAlign: 'center', color: '#7a7060', fontFamily: 'sans-serif', fontSize: '13px', lineHeight: 1.7 }}>
          Services are being updated. Please check back soon.
        </div>
      ) : (
        <Carousel visible={3}>
          {services.map(service => (
            <div
              key={service.id}
              style={{
                background: '#0a0a08',
                padding: '40px 32px',
                minHeight: '260px',
                height: '100%',
              }}
            >
              <div style={{
                width: '32px',
                height: '1px',
                background: '#c9a84c',
                marginBottom: '28px',
              }} />

              <div style={{
                fontSize: '20px',
                color: '#e8e0d0',
                marginBottom: '12px',
              }}>
                {service.name}
              </div>

              <div style={{
                fontSize: '13px',
                color: '#5a5040',
                fontFamily: 'sans-serif',
                lineHeight: 1.8,
                marginBottom: '28px',
              }}>
                {service.description}
              </div>

              <div style={{
                fontSize: '24px',
                color: '#c9a84c',
                fontFamily: 'sans-serif',
              }}>
                {service.price}
              </div>

              <div style={{
                fontSize: '10px',
                color: '#3a3020',
                fontFamily: 'sans-serif',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginTop: '4px',
              }}>
                {service.totalDurationMinutes} min
              </div>
            </div>
          ))}
        </Carousel>
      )}
    </section>
  )
}
