import Hero from '../features/home/components/Hero'
import Stats from '../features/home/components/Stats'
import MastersCarousel from '../features/home/components/MastersCarousel'
import Services from '../features/home/components/Services'
import Cta from '../features/home/components/Cta'
import Footer from '../components/layout/Footer'
import { useHomeMasters } from '../features/home/hooks/useHomeMasters'
import { useHomeStats } from '../features/home/hooks/useHomeStats'
import { useHomeServices } from '../features/home/hooks/useHomeServices'


export default function HomePage() {
  const { data: stats = [] } = useHomeStats()
  const { data: masters = [] } = useHomeMasters()
  const { data: services = [] } = useHomeServices()

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <Hero />
      <Stats stats={stats} />
      <div id="team">
        <MastersCarousel masters={masters} />
      </div>
      <div id="services">
        <Services services={services}/>
      </div>
      <Cta />
      <Footer />
    </div>
  )
}