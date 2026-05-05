import Footer from '../components/layout/Footer'
import CenteredPageLayout from '../components/layout/CenteredPageLayout'
import BookingSuccessHeader from '../features/bookingsuccess/components/BookingSuccessHeader'
import BookingSuccessDetails from '../features/bookingsuccess/components/BookingSuccessDetails'
import BookingSuccessActions from '../features/bookingsuccess/components/BookingSuccessActions'
import BookingSuccessLoading from '../features/bookingsuccess/components/BookingSuccessLoading'
import { useBookingSuccess } from '../features/bookingsuccess/hooks/useBookingSuccess'

export default function BookingSuccessPage() {
  const { bookingId, booking, isLoading} = useBookingSuccess()

  if (isLoading) {
    return <BookingSuccessLoading />
  }

  if (!booking) {
    return null
  }

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <CenteredPageLayout maxWidth="480px" centeredText>
        <BookingSuccessHeader />
        <BookingSuccessDetails bookingId={bookingId} booking={booking} />
        <BookingSuccessActions />
      </CenteredPageLayout>

      <Footer />
    </div>
  )
}