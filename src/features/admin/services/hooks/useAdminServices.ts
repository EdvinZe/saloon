import { useQuery } from '@tanstack/react-query'
import { getAdminServices } from '../api'

export const adminServicesQueryKey = ['admin-services']

export function useAdminServices() {
  return useQuery({
    queryKey: adminServicesQueryKey,
    queryFn: getAdminServices,
    staleTime: 60_000,
  })
}
