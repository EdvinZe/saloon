import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activateAdminService, deactivateAdminService } from '../api'
import { adminServicesQueryKey } from './useAdminServices'

type ToggleAdminServiceVariables = {
  id: number
  nextIsActive: boolean
}

export function useToggleAdminService() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, nextIsActive }: ToggleAdminServiceVariables) => (
      nextIsActive ? activateAdminService(id) : deactivateAdminService(id)
    ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminServicesQueryKey })
      void queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })
}
