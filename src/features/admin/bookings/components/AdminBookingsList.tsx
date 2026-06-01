import type { AdminBooking } from '../types'
import AdminBookingCard from './AdminBookingCard'

type AdminBookingsListProps = {
  bookings: AdminBooking[]
  submittingBookingId: number | null
  onView: (booking: AdminBooking) => void
  onComplete: (booking: AdminBooking) => void
  onNoShow: (booking: AdminBooking) => void
  onCancel: (booking: AdminBooking) => void
}

export default function AdminBookingsList({
  bookings,
  submittingBookingId,
  onView,
  onComplete,
  onNoShow,
  onCancel,
}: AdminBookingsListProps) {
  if (bookings.length === 0) {
    return (
      <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
        No bookings found
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {bookings.map(booking => (
        <AdminBookingCard
          key={booking.id}
          booking={booking}
          isSubmitting={submittingBookingId === booking.id}
          onView={onView}
          onComplete={onComplete}
          onNoShow={onNoShow}
          onCancel={onCancel}
        />
      ))}
    </div>
  )
}
