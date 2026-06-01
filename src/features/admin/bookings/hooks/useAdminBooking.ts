import { useQuery } from '@tanstack/react-query'
import { getAdminBooking } from '../api'

export const adminBookingQueryKey = (id: number | null) => ['admin-booking', id]

export function useAdminBooking(id: number | null) {
  return useQuery({
    queryKey: adminBookingQueryKey(id),
    queryFn: () => getAdminBooking(id!),
    enabled: Boolean(id),
    staleTime: 30_000,
  })
}
