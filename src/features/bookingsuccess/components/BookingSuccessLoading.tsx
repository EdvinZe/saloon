import Footer from '../../../components/layout/Footer'
import CenteredPageLayout from '../../../components/layout/CenteredPageLayout'

export default function BookingSuccessLoading() {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <CenteredPageLayout maxWidth="480px" centeredText>
        <p style={{
          color: '#7a7060',
          fontFamily: 'sans-serif',
          letterSpacing: '3px',
        }}>
          Loading booking...
        </p>
      </CenteredPageLayout>

      <Footer />
    </div>
  )
}