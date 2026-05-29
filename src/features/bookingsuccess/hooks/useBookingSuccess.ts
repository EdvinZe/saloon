import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getBookingPaymentResult } from '../api'

const MAX_PAYMENT_RESULT_ATTEMPTS = 5
const PAYMENT_RESULT_POLL_MS = 1800

export function useBookingSuccess() {
  const [params] = useSearchParams()
  const paymentIntentId = params.get('payment_intent')?.trim() ?? ''
  const redirectStatus = params.get('redirect_status')
  const hasInvalidRedirectStatus = Boolean(
    redirectStatus && redirectStatus !== 'succeeded'
  )

  const query = useQuery({
    queryKey: ['booking-payment-result', paymentIntentId],
    queryFn: () => getBookingPaymentResult(paymentIntentId),
    enabled: Boolean(paymentIntentId) && !hasInvalidRedirectStatus,
    staleTime: 0,
    refetchInterval: result => {
      if (result.state.data?.status !== 'processing') {
        return false
      }

      if (result.state.dataUpdateCount >= MAX_PAYMENT_RESULT_ATTEMPTS) {
        return false
      }

      return PAYMENT_RESULT_POLL_MS
    },
  })

  const isMissingPaymentIntent = !paymentIntentId
  const isProcessing = query.data?.status === 'processing'
  const isProcessingTimeout =
    isProcessing && query.dataUpdateCount >= MAX_PAYMENT_RESULT_ATTEMPTS
  const isNotFound = query.data?.status === 'not_found'
  const isError =
    isMissingPaymentIntent ||
    hasInvalidRedirectStatus ||
    isNotFound ||
    isProcessingTimeout ||
    query.isError

  return {
    paymentIntentId,
    booking: query.data?.status === 'confirmed' ? query.data.booking : null,
    isLoading: query.isLoading,
    isProcessing,
    isError,
    errorReason: isMissingPaymentIntent
      ? 'missing_payment_intent'
      : hasInvalidRedirectStatus
        ? redirectStatus === 'canceled'
          ? 'cancelled'
          : 'failed'
        : isProcessingTimeout
          ? 'processing_timeout'
          : isNotFound
            ? 'not_found'
            : query.isError
              ? 'lookup_failed'
              : null,
  }
}
