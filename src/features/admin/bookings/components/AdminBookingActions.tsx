import type { AdminBooking } from '../types'

type AdminBookingActionsProps = {
  booking: AdminBooking
  isSubmitting: boolean
  onComplete: (booking: AdminBooking) => void
  onNoShow: (booking: AdminBooking) => void
  onCancel: (booking: AdminBooking) => void
}

export default function AdminBookingActions({
  booking,
  isSubmitting,
  onComplete,
  onNoShow,
  onCancel,
}: AdminBookingActionsProps) {
  if (booking.status !== 'confirmed') {
    return (
      <span className="text-xs uppercase tracking-[0.18em] text-[#7a7060]">
        {booking.status.replace('_', ' ')}
      </span>
    )
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={() => onComplete(booking)} disabled={isSubmitting}>
        Complete
      </button>
      <button
        type="button"
        className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
        onClick={() => onNoShow(booking)}
        disabled={isSubmitting}
      >
        No-show
      </button>
      <button
        type="button"
        className="border border-rose-500/40 px-4 py-2 text-xs uppercase tracking-[0.18em] text-rose-100 hover:bg-rose-500/10"
        onClick={() => onCancel(booking)}
        disabled={isSubmitting}
      >
        Cancel & refund
      </button>
    </div>
  )
}
