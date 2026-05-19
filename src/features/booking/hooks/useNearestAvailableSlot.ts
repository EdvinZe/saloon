import { useQuery } from '@tanstack/react-query'
import { getNearestAvailableSlot } from '../api'

export function useNearestAvailableSlot(serviceId: number) {
  return useQuery({
    queryKey: ['nearest-available-slot', serviceId],
    queryFn: () => getNearestAvailableSlot(serviceId),
    enabled: !!serviceId,
    staleTime: 60_000,
  })
}
