import { useQuery } from '@tanstack/react-query'
import { getHomeMetrics } from '../api'
import { buildHomeStats } from '../utils/homeStats'

export function useHomeStats() {
  return useQuery({
    queryKey: ['home-stats'],
    queryFn: getHomeMetrics,
    select: buildHomeStats,
    staleTime: 5 * 60_000,
  })
}