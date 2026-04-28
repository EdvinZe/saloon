import { useQuery } from '@tanstack/react-query'
import { getAvailableSlots } from '../api'
import type { SlotStatus } from '../api'

export function useAvailableSlots(date: string | null) {
  return useQuery<SlotStatus[]>({
    queryKey: ['slots', date],
    queryFn: () => getAvailableSlots(date!),
    enabled: !!date,
    placeholderData: [],
    staleTime: 60_000,
  })
}
