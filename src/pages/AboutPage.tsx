import Footer from '../components/layout/Footer'
import AboutHero from '../features/about/components/AboutHero'
import AboutStory from '../features/about/components/AboutStory'
import AboutTeam from '../features/about/components/AboutTeam'
import AboutContact from '../features/about/components/AboutContact'
import LoadableSection from '../shared/components/LoadableSection'

export default function AboutPage() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', color: '#e8e0d0' }}>
      <AboutHero />
      <AboutStory />

      <LoadableSection id="team" minHeight="420px">
        <AboutTeam />
      </LoadableSection>

      <LoadableSection id="contact" minHeight="420px">
        <AboutContact />
      </LoadableSection>

      <Footer />
    </div>
  )
}