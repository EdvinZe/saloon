import { useQuery } from '@tanstack/react-query'
import { getAvailableSlotsForService } from '../../bookingavailability/api'

export function useManageAvailableSlots(
  date: string | null,
  serviceId: string | null,
  excludeBookingToken?: string | null,
) {
  return useQuery({
    queryKey: ['manage-booking-slots', date, serviceId, excludeBookingToken],
    queryFn: () => getAvailableSlotsForService({
      date: date!,
      serviceId: serviceId!,
      excludeBookingToken: excludeBookingToken ?? undefined,
    }),
    enabled: !!date && !!serviceId,
    staleTime: 60_000,
  })
}
