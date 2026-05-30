import { useQuery } from '@tanstack/react-query'
import { getAvailableMastersForSlot } from '../../bookingavailability/api'

export function useManageAvailableMasters(
  date: string | null,
  time: string | null,
  serviceId: number | null,
) {
  return useQuery({
    queryKey: ['manage-available-masters', date, time, serviceId],
    queryFn: () => getAvailableMastersForSlot({ date: date!, time: time!, serviceId: serviceId! }),
    enabled: !!date && !!time && !!serviceId,
    staleTime: 60_000,
  })
}
