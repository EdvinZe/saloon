import type { Master } from '../../../shared/data/mockData'
import Carousel from '../../../components/ui/Carousel'

interface MastersCarouselProps {
  masters: Master[]
}

export default function MastersCarousel({ masters }: MastersCarouselProps) {
  return (
    <section style={{ padding: '80px 48px', borderBottom: '1px solid #2a2218' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <p style={{
          fontSize: '10px',
          letterSpacing: '5px',
          color: '#c9a84c',
          textTransform: 'uppercase',
          fontFamily: 'sans-serif',
          marginBottom: '16px',
        }}>
          The team
        </p>

        <h2 style={{ fontSize: '34px', color: '#e8e0d0', fontWeight: 400 }}>
          Meet your barber
        </h2>
      </div>

      <Carousel visible={3}>
        {masters.map(master => (
          <div
            key={master.id}
            style={{
              background: '#141008',
              padding: '40px 32px',
              textAlign: 'center',
              height: '100%',
            }}
          >
            <div style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              border: '1px solid #3a3020',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '22px',
              color: '#c9a84c',
              fontFamily: 'sans-serif',
              margin: '0 auto 24px',
            }}>
              {master.initials}
            </div>

            <div style={{ fontSize: '18px', color: '#e8e0d0', marginBottom: '6px' }}>
              {master.name}
            </div>

            <div style={{
              fontSize: '10px',
              color: '#c9a84c',
              letterSpacing: '3px',
              textTransform: 'uppercase',
              fontFamily: 'sans-serif',
              marginBottom: '16px',
            }}>
              {master.role}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
              {master.tags.map(tag => (
                <span
                  key={tag}
                  style={{
                    fontSize: '10px',
                    color: '#7a7060',
                    fontFamily: 'sans-serif',
                    border: '1px solid #2a2218',
                    padding: '4px 10px',
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </Carousel>
    </section>
  )
}