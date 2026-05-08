import Footer from '../components/layout/Footer'
import { useBookingError } from '../features/bookingerror/hooks/useBookingError'
import BookingErrorContent from '../features/bookingerror/components/BookingErrorContent'

export default function BookingErrorPage() {
  const config = useBookingError()

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <BookingErrorContent config={config} />
      <Footer />
    </div>
  )
}
