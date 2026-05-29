export interface ErrorConfig {
  title: string
  sub: string
  btn: string
  btnHref: string
  secondaryBtn?: string
  secondaryHref?: string
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
  'payment_result.missing_payment_intent': {
    title: 'Booking not found',
    sub: 'We could not confirm this booking because the payment reference is missing.',
    btn: 'Back to booking →',
    btnHref: '/booking',
  },
  'payment_result.cancelled': {
    title: 'Payment cancelled',
    sub: 'Your payment was cancelled. No booking has been confirmed.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
  'payment_result.failed': {
    title: 'Payment failed',
    sub: 'Stripe did not return a successful payment status. No booking has been confirmed.',
    btn: 'Try again →',
    btnHref: '/booking',
  },
  'payment_result.processing_timeout': {
    title: 'Confirmation delayed',
    sub: 'Payment was received, but booking confirmation is taking longer than expected. Please contact support.',
    btn: 'Back to home →',
    btnHref: '/',
  },
  'payment_result.not_found': {
    title: 'Booking not found',
    sub: 'We could not find a confirmed booking for this payment.',
    btn: 'Back to booking →',
    btnHref: '/booking',
  },
  'payment_result.lookup_failed': {
    title: 'Confirmation unavailable',
    sub: 'We could not check your booking confirmation right now. Please contact support if your payment went through.',
    btn: 'Back to home →',
    btnHref: '/',
  },
  'page.not_found': {
    title: 'Page not found',
    sub: 'The page you are looking for does not exist or may have been moved.',
    btn: 'Back to home →',
    btnHref: '/',
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
  const key =
    type === 'payment_failed' || type === 'payment_result' || type === 'page'
      ? `${type}.${reason}`
      : type
  return ERROR_MAP[key] ?? ERROR_MAP['default']
}
