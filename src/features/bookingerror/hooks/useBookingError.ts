import { useSearchParams } from 'react-router-dom'
import { getBookingErrorConfig } from '../config/bookingErrorConfig'

export function useBookingError() {
  const [params] = useSearchParams()
  const type = params.get('type') ?? ''
  const reason = params.get('reason') ?? ''

  return getBookingErrorConfig(type, reason)
}
