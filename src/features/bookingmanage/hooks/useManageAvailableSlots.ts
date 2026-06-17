import { useQuery } from '@tanstack/react-query'
import { getAvailableSlotsForService } from '../../bookingavailability/api'

export function useManageAvailableSlots(
  date: string | null,
  serviceId: number | null,
) {
  return useQuery({
    queryKey: ['manage-booking-slots', date, serviceId],
    queryFn: () => getAvailableSlotsForService({
      date: date!,
      serviceId: serviceId!,
    }),
    enabled: !!date && !!serviceId,
    staleTime: 60_000,
  })
}
