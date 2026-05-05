import { useQuery } from '@tanstack/react-query'
import { getHomeMasters } from '../api'

export function useHomeMasters() {
  return useQuery({
    queryKey: ['home-masters'],
    queryFn: getHomeMasters,
    staleTime: 5 * 60_000,
  })
}