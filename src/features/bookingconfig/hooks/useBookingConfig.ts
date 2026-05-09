import { useQuery } from '@tanstack/react-query'
import { getBookingConfig } from '../api'

export function useBookingConfig() {
  return useQuery({
    queryKey: ['booking-config'],
    queryFn: getBookingConfig,
    staleTime: 10 * 60_000,
  })
}
