import Footer from '../components/layout/Footer'
import { useBookingError } from '../features/bookingerror/hooks/useBookingError'
import BookingErrorContent from '../features/bookingerror/components/BookingErrorContent'

interface Props {
  forcedType?: string
  forcedReason?: string
}

export default function BookingErrorPage({ forcedType, forcedReason }: Props) {
  const config = useBookingError({ forcedType, forcedReason })

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <BookingErrorContent config={config} />
      <Footer />
    </div>
  )
}
