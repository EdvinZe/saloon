import WorksGallery from '../features/works/components/WorksGallery'
import Footer from '../components/layout/Footer'
import WorksHeader from '../features/works/components/WorksHeader'

export default function WorksPage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
        <WorksHeader />

      <div style={{ padding: '48px' }}>
        <WorksGallery />
      </div>

      <Footer />
    </div>
  )
}
