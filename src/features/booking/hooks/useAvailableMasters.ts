import { useQuery } from '@tanstack/react-query'
import { getAvailableMasters } from '../api'
import type { Master } from '../../../shared/data/mockData'

export function useAvailableMasters(date: string | null, time: string | null) {
  return useQuery<Master[]>({
    queryKey: ['masters', date, time],
    queryFn: () => getAvailableMasters(date!, time!),
    enabled: !!date && !!time,
    placeholderData: [],
    staleTime: 60_000,
  })
}
