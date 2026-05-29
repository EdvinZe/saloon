import Footer from '../../../components/layout/Footer'
import CenteredPageLayout from '../../../components/layout/CenteredPageLayout'

interface Props {
  message?: string
}

export default function BookingSuccessLoading({ message = 'Loading booking...' }: Props) {
  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <CenteredPageLayout maxWidth="480px" centeredText>
        <p style={{
          color: '#7a7060',
          fontFamily: 'sans-serif',
          letterSpacing: '3px',
        }}>
          {message}
        </p>
      </CenteredPageLayout>

      <Footer />
    </div>
  )
}
