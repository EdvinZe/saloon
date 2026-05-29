import { Navigate } from 'react-router-dom'
import Footer from '../components/layout/Footer'
import CenteredPageLayout from '../components/layout/CenteredPageLayout'
import BookingSuccessHeader from '../features/bookingsuccess/components/BookingSuccessHeader'
import BookingSuccessDetails from '../features/bookingsuccess/components/BookingSuccessDetails'
import BookingSuccessActions from '../features/bookingsuccess/components/BookingSuccessActions'
import BookingSuccessLoading from '../features/bookingsuccess/components/BookingSuccessLoading'
import { useBookingSuccess } from '../features/bookingsuccess/hooks/useBookingSuccess'

export default function BookingSuccessPage() {
  const { booking, isLoading, isProcessing, isError, errorReason } = useBookingSuccess()

  if (isLoading) {
    return <BookingSuccessLoading message="Confirming your booking..." />
  }

  if (isProcessing) {
    return (
      <BookingSuccessLoading message="Payment received. We are confirming your booking..." />
    )
  }

  if (isError) {
    return (
      <Navigate
        replace
        to={`/booking/error?type=payment_result&reason=${errorReason ?? 'lookup_failed'}`}
      />
    )
  }

  if (!booking) {
    return null
  }

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <CenteredPageLayout maxWidth="480px" centeredText>
        <BookingSuccessHeader />
        <BookingSuccessDetails booking={booking} />
        <BookingSuccessActions manageUrl={booking.manage_url} />
      </CenteredPageLayout>

      <Footer />
    </div>
  )
}
