import { useQuery } from '@tanstack/react-query'
import { getMasters } from '../api'

export function useMasters(serviceId?: number) {
  return useQuery({
    queryKey: ['masters', serviceId ?? null],
    queryFn: () => getMasters(serviceId),
    staleTime: 5 * 60_000,
  })
}
