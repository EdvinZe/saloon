import Footer from '../components/layout/Footer'
import AboutContact from '../features/about/components/AboutContact'
import AboutHero from '../features/about/components/AboutHero'
import AboutStory from '../features/about/components/AboutStory'
import AboutTeam from '../features/about/components/AboutTeam'

export default function AboutPage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', color: '#e8e0d0' }}>

      <AboutHero />

      <AboutStory />

      <AboutTeam />

      <AboutContact />

      <Footer />
    </div>
  )
}
