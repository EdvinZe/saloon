import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activateAdminMaster, deactivateAdminMaster } from '../api'
import { adminMastersQueryKey } from './useAdminMasters'

type ToggleAdminMasterVariables = {
  id: number
  nextIsActive: boolean
}

export function useToggleAdminMaster() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, nextIsActive }: ToggleAdminMasterVariables) => (
      nextIsActive ? activateAdminMaster(id) : deactivateAdminMaster(id)
    ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminMastersQueryKey })
      void queryClient.invalidateQueries({ queryKey: ['masters'] })
      void queryClient.invalidateQueries({ queryKey: ['available-masters'] })
      void queryClient.invalidateQueries({ queryKey: ['manage-available-masters'] })
      void queryClient.invalidateQueries({ queryKey: ['booking-slots'] })
      void queryClient.invalidateQueries({ queryKey: ['manage-booking-slots'] })
    },
  })
}
