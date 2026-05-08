import { useQuery } from '@tanstack/react-query'
import { getServices } from '../api'

export function useServices() {
  return useQuery({
    queryKey: ['services'],
    queryFn: getServices,
    staleTime: 5 * 60_000,
  })
}