import Hero from '../features/home/components/Hero'
import Stats from '../features/home/components/Stats'
import MastersCarousel from '../features/home/components/MastersCarousel'
import Services from '../features/home/components/Services'
import Cta from '../features/home/components/Cta'
import Footer from '../components/layout/Footer'
import { MOCK_MASTERS } from '../shared/data/mockData'

export default function HomePage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <Hero />
      <Stats />
      <div id="team">
        <MastersCarousel masters={MOCK_MASTERS} />
      </div>
      <div id="services">
        <Services />
      </div>
      <Cta />
      <Footer />
    </div>
  )
}