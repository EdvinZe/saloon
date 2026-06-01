import { useQuery } from '@tanstack/react-query'
import { getAdminBookings } from '../api'
import type { AdminBookingListParams } from '../types'

export const adminBookingsQueryKey = (params?: AdminBookingListParams) => [
  'admin-bookings',
  params?.date ?? null,
  params?.status ?? null,
  params?.masterId ?? null,
  params?.serviceId ?? null,
]

export function useAdminBookings(params: AdminBookingListParams) {
  return useQuery({
    queryKey: adminBookingsQueryKey(params),
    queryFn: () => getAdminBookings(params),
    staleTime: 30_000,
  })
}
