import { format } from 'date-fns'
import type { AdminBooking } from '../types'
import AdminBookingStatusBadge from './AdminBookingStatusBadge'

type AdminBookingDetailsModalProps = {
  booking: AdminBooking
  onClose: () => void
}

function formatPrice(amountCents: number, currency: string) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amountCents / 100)
}

export default function AdminBookingDetailsModal({
  booking,
  onClose,
}: AdminBookingDetailsModalProps) {
  const customerName = `${booking.customer_first_name} ${booking.customer_last_name}`

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto border border-[#2a2218] bg-[#141008] p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#c9a84c]">Booking details</p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">{booking.booking_code ?? `Booking #${booking.id}`}</h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          <Detail label="Customer" value={customerName} />
          <Detail label="Phone" value={booking.customer_phone} />
          <Detail label="Email" value={booking.customer_email} />
          <Detail label="Service" value={booking.service_name ?? `Service #${booking.service_id}`} />
          <Detail label="Master" value={booking.master_name ?? `Master #${booking.master_id}`} />
          <Detail label="Start" value={format(new Date(booking.start_at), 'yyyy-MM-dd HH:mm')} />
          <Detail label="End" value={format(new Date(booking.end_at), 'yyyy-MM-dd HH:mm')} />
          <Detail label="Source" value={booking.source} />
          <Detail label="Deposit" value={`${formatPrice(booking.deposit_amount_cents, booking.currency)} · ${booking.deposit_status}`} />
          <Detail label="Payment intent" value={booking.stripe_payment_intent_id ?? 'None'} />
          <Detail label="Checkout session" value={booking.stripe_checkout_session_id ?? 'None'} />
          <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
            <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">Status</dt>
            <dd className="mt-2"><AdminBookingStatusBadge status={booking.status} /></dd>
          </div>
        </div>
      </div>
    </div>
  )
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
      <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">{label}</dt>
      <dd className="mt-1 break-words text-sm text-[#e8e0d0]">{value}</dd>
    </div>
  )
}
