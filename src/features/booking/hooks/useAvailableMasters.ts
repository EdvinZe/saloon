import { useQuery } from '@tanstack/react-query'
import { getAvailableMastersForSlot } from '../../bookingavailability/api'
import type { Master } from '../../masters/api'

export function useAvailableMasters(date: string | null, time: string | null, serviceId: number | null) {
  return useQuery<Master[]>({
    queryKey: ['available-masters', date, time, serviceId],
    queryFn: () => getAvailableMastersForSlot({ date: date!, time: time!, serviceId: serviceId! }),
    enabled: !!date && !!time && !!serviceId,
    placeholderData: [],
    staleTime: 60_000,
  })
}
