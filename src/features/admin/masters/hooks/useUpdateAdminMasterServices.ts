import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminMasterServices } from '../api'
import { adminMastersQueryKey } from './useAdminMasters'

type UpdateAdminMasterServicesVariables = {
  id: number
  serviceIds: number[]
}

export function useUpdateAdminMasterServices() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, serviceIds }: UpdateAdminMasterServicesVariables) => (
      updateAdminMasterServices(id, serviceIds)
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
