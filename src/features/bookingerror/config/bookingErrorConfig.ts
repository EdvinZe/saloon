export interface ErrorConfig {
  title: string
  sub: string
  btn: string
  btnHref: string
}

// Keyed by `type` or `payment_failed.{reason}` for payment sub-types
export const ERROR_MAP: Record<string, ErrorConfig> = {
  'payment_failed.card_declined': {
    title: 'Payment failed',
    sub: "We couldn't process your payment — your card was declined. Please try a different card or contact your bank.",
    btn: 'Try another card →',
    btnHref: '/booking',
  },
  'payment_failed.insufficient_funds': {
    title: 'Payment failed',
    sub: "We couldn't process your payment — insufficient funds on your card. Please try a different card.",
    btn: 'Try another card →',
    btnHref: '/booking',
  },
  session_expired: {
    title: 'Slot just taken',
    sub: 'Someone booked this time slot while you were checking out. Please go back and choose another time.',
    btn: 'Choose another time →',
    btnHref: '/booking',
  },
  stripe_error: {
    title: 'Something went wrong',
    sub: 'We had a technical issue on our end. Your card was not charged. Please try again.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
  booking_cancelled: {
    title: 'Booking cancelled',
    sub: 'Your booking was cancelled by the barber. Please choose another time or a different barber.',
    btn: 'Book again →',
    btnHref: '/booking',
  },
  default: {
    title: 'Something went wrong',
    sub: 'An unexpected error occurred. Your card was not charged. Please try again.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
}

export function getBookingErrorConfig(type: string, reason: string) {
  const key = type === 'payment_failed' ? `payment_failed.${reason}` : type
  return ERROR_MAP[key] ?? ERROR_MAP['default']
}
