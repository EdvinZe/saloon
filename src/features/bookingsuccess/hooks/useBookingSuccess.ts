import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { getBookingPaymentResult } from '../api'

const MAX_PAYMENT_RESULT_ATTEMPTS = 5
const PAYMENT_RESULT_POLL_MS = 1800

export function useBookingSuccess() {
  const [params] = useSearchParams()
  const paymentIntentId = params.get('payment_intent')?.trim() ?? ''
  const redirectStatus = params.get('redirect_status')
  const [paymentResultAttempts, setPaymentResultAttempts] = useState(0)
  const hasInvalidRedirectStatus = Boolean(
    redirectStatus && redirectStatus !== 'succeeded'
  )
  const canCheckPaymentResult = Boolean(paymentIntentId) && !hasInvalidRedirectStatus

  useEffect(() => {
    setPaymentResultAttempts(0)
  }, [paymentIntentId, redirectStatus])

  const query = useQuery({
    queryKey: ['booking-payment-result', paymentIntentId],
    queryFn: () => {
      setPaymentResultAttempts(attempts => attempts + 1)
      return getBookingPaymentResult(paymentIntentId)
    },
    enabled: canCheckPaymentResult && paymentResultAttempts < MAX_PAYMENT_RESULT_ATTEMPTS,
    staleTime: 0,
    retry: false,
    refetchOnWindowFocus: false,
    refetchInterval: result => {
      if (result.state.data?.status !== 'processing') {
        return false
      }

      if (paymentResultAttempts >= MAX_PAYMENT_RESULT_ATTEMPTS) {
        return false
      }

      return PAYMENT_RESULT_POLL_MS
    },
  })

  const isMissingPaymentIntent = !paymentIntentId
  const isProcessingTimeout =
    query.data?.status === 'processing' &&
    paymentResultAttempts >= MAX_PAYMENT_RESULT_ATTEMPTS
  const isProcessing =
    query.data?.status === 'processing' && !isProcessingTimeout
  const isConfirmedWithoutBooking =
    query.data?.status === 'confirmed' && !query.data.booking
  const isNotFound = query.data?.status === 'not_found'
  const isPaymentFailed = query.data?.status === 'failed'
  const isLookupFailed = query.data?.status === 'lookup_failed'
  const isRecoveryFailed = query.data?.status === 'recovery_failed'
  const isError =
    isMissingPaymentIntent ||
    hasInvalidRedirectStatus ||
    isConfirmedWithoutBooking ||
    isNotFound ||
    isPaymentFailed ||
    isLookupFailed ||
    isRecoveryFailed ||
    isProcessingTimeout ||
    query.isError

  return {
    paymentIntentId,
    booking: query.data?.status === 'confirmed' && query.data.booking ? query.data.booking : null,
    isLoading: query.isLoading,
    isProcessing,
    isError,
    errorReason: isMissingPaymentIntent
      ? 'missing_payment_intent'
      : hasInvalidRedirectStatus
        ? redirectStatus === 'canceled' || redirectStatus === 'cancelled'
          ? 'cancelled'
          : 'failed'
          : isProcessingTimeout
            ? 'processing_timeout'
            : isNotFound
              ? 'not_found'
              : isPaymentFailed
                ? 'failed'
                : isLookupFailed
                  ? 'lookup_failed'
                  : isRecoveryFailed
                    ? 'recovery_failed'
                    : query.isError || isConfirmedWithoutBooking
                      ? 'lookup_failed'
                      : null,
  }
}
