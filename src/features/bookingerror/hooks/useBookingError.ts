import { useSearchParams } from 'react-router-dom'
import { getBookingErrorConfig } from '../config/bookingErrorConfig'

interface UseBookingErrorOptions {
  forcedType?: string
  forcedReason?: string
}

export function useBookingError(options: UseBookingErrorOptions = {}) {
  const [params] = useSearchParams()
  const type = options.forcedType ?? params.get('type') ?? ''
  const reason = options.forcedReason ?? params.get('reason') ?? ''

  return getBookingErrorConfig(type, reason)
}
