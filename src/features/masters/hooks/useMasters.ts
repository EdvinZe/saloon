import { useQuery } from '@tanstack/react-query'
import { getMasters } from '../api'

export function useMasters() {
  return useQuery({
    queryKey: ['masters'],
    queryFn: getMasters,
    staleTime: 5 * 60_000,
  })
}
