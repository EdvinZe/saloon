import { useQuery } from '@tanstack/react-query'
import { getHomeServices } from '../api'

export function useHomeServices() {
  return useQuery({
    queryKey: ['home-services'],
    queryFn: getHomeServices,
    staleTime: 5 * 60_000,
  })
}