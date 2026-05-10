import { useQuery } from '@tanstack/react-query'
import { getAvailableMastersForSlot } from '../../bookingavailability/api'

export function useManageAvailableMasters(
  date: string | null,
  time: string | null,
  durationMin: number | null,
) {
  return useQuery({
    queryKey: ['manage-available-masters', date, time, durationMin],
    queryFn: () => getAvailableMastersForSlot({ date: date!, time: time!, durationMin: durationMin! }),
    enabled: !!date && !!time && !!durationMin,
    staleTime: 60_000,
  })
}
