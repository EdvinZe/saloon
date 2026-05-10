import { useQuery } from '@tanstack/react-query'
import { getAvailableSlotsForService } from '../../bookingavailability/api'
import type { AvailableSlotStatus } from '../../bookingavailability/api'

export function useAvailableSlots(date: string | null, serviceId: string | null) {
  return useQuery<AvailableSlotStatus[]>({
    queryKey: ['booking-slots', date, serviceId],
    queryFn: () => getAvailableSlotsForService({ date: date!, serviceId: serviceId! }),
    enabled: !!date && !!serviceId,
    placeholderData: [],
    staleTime: 60_000,
  })
}
