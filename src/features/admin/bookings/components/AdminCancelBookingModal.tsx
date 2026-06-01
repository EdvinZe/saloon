import type { AdminBooking } from '../types'

type AdminCancelBookingModalProps = {
  booking: AdminBooking
  isCancelling: boolean
  errorMessage?: string | null
  onClose: () => void
  onConfirm: (booking: AdminBooking) => void
}

export default function AdminCancelBookingModal({
  booking,
  isCancelling,
  errorMessage,
  onClose,
  onConfirm,
}: AdminCancelBookingModalProps) {
  const customerName = `${booking.customer_first_name} ${booking.customer_last_name}`
  const isPaid = booking.deposit_status === 'paid'
  const title = isPaid
    ? 'Cancel this booking and refund the deposit?'
    : 'Cancel this booking?'
  const body = isPaid
    ? 'The deposit will be refunded to the original payment method.'
    : 'This booking will be cancelled without changing the deposit to refunded.'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="w-full max-w-lg border border-[#2a2218] bg-[#141008] p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-rose-300">Cancel booking</p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">{title}</h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <p className="mt-4 text-sm text-[#e8e0d0]">
          {booking.booking_code ?? `Booking #${booking.id}`} for {customerName}
        </p>
        <p className="mt-3 text-sm text-[#7a7060]">
          {body}
        </p>

        {errorMessage ? <p className="mt-4 text-sm text-rose-300">{errorMessage}</p> : null}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="px-4 py-2 text-sm text-[#7a7060]" onClick={onClose}>
            Keep booking
          </button>
          <button
            type="button"
            className="border border-rose-500/40 px-5 py-2 text-xs uppercase tracking-[0.18em] text-rose-100 hover:bg-rose-500/10"
            onClick={() => onConfirm(booking)}
            disabled={isCancelling}
          >
            {isCancelling ? 'Cancelling...' : isPaid ? 'Cancel & refund' : 'Cancel booking'}
          </button>
        </div>
      </div>
    </div>
  )
}
