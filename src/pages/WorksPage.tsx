import WorksGallery from '../features/works/components/WorksGallery'
import Footer from '../components/layout/Footer'

export default function WorksPage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <div style={{
        textAlign: 'center',
        padding: '72px 48px 56px',
        borderBottom: '1px solid #2a2218',
      }}>
        <p style={{
          color: '#c9a84c',
          fontSize: '11px',
          letterSpacing: '4px',
          textTransform: 'uppercase',
          fontFamily: 'sans-serif',
          marginBottom: '18px',
        }}>
          Portfolio
        </p>
        <h1 style={{
          color: '#e8e0d0',
          fontSize: '38px',
          fontFamily: 'Georgia, serif',
          fontWeight: 400,
          letterSpacing: '2px',
          marginBottom: '16px',
        }}>
          Our work
        </h1>
        <p style={{
          color: '#7a7060',
          fontSize: '14px',
          fontFamily: 'sans-serif',
          letterSpacing: '1px',
        }}>
          Every cut tells a story
        </p>
      </div>

      <div style={{ padding: '48px' }}>
        <WorksGallery />
      </div>

      <Footer />
    </div>
  )
}
