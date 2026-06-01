import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createAdminService } from '../api'
import { adminServicesQueryKey } from './useAdminServices'

export function useCreateAdminService() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createAdminService,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminServicesQueryKey })
      void queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })
}
