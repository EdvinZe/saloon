import Hero from '../features/home/components/Hero'
import HomeStatsSection from '../features/home/components/HomeStatsSection'
import HomeMastersSection from '../features/home/components/HomeMastersSection'
import HomeServicesSection from '../features/home/components/HomeServicesSection'
import Cta from '../features/home/components/Cta'
import Footer from '../components/layout/Footer'
import LoadableSection from '../shared/components/LoadableSection'

export default function HomePage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <Hero />

      <LoadableSection minHeight="160px">
        <HomeStatsSection />
      </LoadableSection>

      <LoadableSection id="team" minHeight="360px">
        <HomeMastersSection />
      </LoadableSection>

      <LoadableSection id="services" minHeight="360px">
        <HomeServicesSection />
      </LoadableSection>

      <Cta />
      <Footer />
    </div>
  )
}