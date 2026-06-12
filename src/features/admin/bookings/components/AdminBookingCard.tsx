import { format } from 'date-fns'
import type { AdminBooking } from '../types'
import AdminBookingActions from './AdminBookingActions'
import AdminBookingStatusBadge from './AdminBookingStatusBadge'

type AdminBookingCardProps = {
  booking: AdminBooking
  isSubmitting: boolean
  onView: (booking: AdminBooking) => void
  onComplete: (booking: AdminBooking) => void
  onNoShow: (booking: AdminBooking) => void
  onCancel: (booking: AdminBooking) => void
}

function formatPrice(amountCents: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amountCents / 100)
}

function formatDateTimeRange(booking: AdminBooking) {
  const start = new Date(booking.start_at)
  const end = new Date(booking.end_at)

  return `${format(start, 'yyyy-MM-dd HH:mm')} - ${format(end, 'HH:mm')}`
}

export default function AdminBookingCard({
  booking,
  isSubmitting,
  onView,
  onComplete,
  onNoShow,
  onCancel,
}: AdminBookingCardProps) {
  const customerName = `${booking.customer_first_name} ${booking.customer_last_name}`

  return (
    <article className="border border-[#2a2218] bg-[#141008] p-4">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="break-words text-xl text-[#e8e0d0]">{formatDateTimeRange(booking)}</h2>
            <AdminBookingStatusBadge status={booking.status} />
            <span className="border border-[#2a2218] bg-[#0f0f0f] px-2 py-1 text-[11px] uppercase tracking-[0.16em] text-[#7a7060]">
              {booking.deposit_status}
            </span>
          </div>
          <p className="mt-3 break-words text-sm text-[#e8e0d0]">
            {booking.service_name ?? `Service #${booking.service_id}`} with {booking.master_name ?? `Master #${booking.master_id}`}
          </p>
          <p className="mt-1 break-words text-sm text-[#7a7060]">
            {customerName} · {booking.customer_phone} · {booking.customer_email}
          </p>
          <p className="mt-1 break-words text-xs uppercase tracking-[0.16em] text-[#5a5040]">
            {booking.booking_code ?? `Booking #${booking.id}`} · {formatPrice(booking.deposit_amount_cents, booking.currency)}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
            onClick={() => onView(booking)}
          >
            Details
          </button>
          <AdminBookingActions
            booking={booking}
            isSubmitting={isSubmitting}
            onComplete={onComplete}
            onNoShow={onNoShow}
            onCancel={onCancel}
          />
        </div>
      </div>
    </article>
  )
}
