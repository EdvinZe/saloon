import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getBookingSuccess } from '../api'

export function useBookingSuccess() {
  const [params] = useSearchParams()
  const bookingId = params.get('booking_id')

  const query = useQuery({
    queryKey: ['booking-success', bookingId],
    queryFn: () => getBookingSuccess(bookingId ?? 'mock-booking'),
    staleTime: 60_000,
  })

  return {
    bookingId,
    booking: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
  }
}