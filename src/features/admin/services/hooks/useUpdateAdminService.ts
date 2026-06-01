import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminService } from '../api'
import { adminServicesQueryKey } from './useAdminServices'
import type { AdminServiceUpdateInput } from '../types'

type UpdateAdminServiceVariables = {
  id: number
  payload: AdminServiceUpdateInput
}

export function useUpdateAdminService() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: UpdateAdminServiceVariables) => updateAdminService(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminServicesQueryKey })
      void queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })
}
