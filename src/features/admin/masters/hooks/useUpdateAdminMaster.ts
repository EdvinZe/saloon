import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminMaster } from '../api'
import { adminMastersQueryKey } from './useAdminMasters'
import type { AdminMasterUpdateInput } from '../types'

type UpdateAdminMasterVariables = {
  id: number
  payload: AdminMasterUpdateInput
}

export function useUpdateAdminMaster() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: UpdateAdminMasterVariables) => updateAdminMaster(id, payload),
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
