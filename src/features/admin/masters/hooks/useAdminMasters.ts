import { useQuery } from '@tanstack/react-query'
import { getAdminMasters } from '../api'

export const adminMastersQueryKey = ['admin-masters']

export function useAdminMasters() {
  return useQuery({
    queryKey: adminMastersQueryKey,
    queryFn: getAdminMasters,
    staleTime: 60_000,
  })
}
