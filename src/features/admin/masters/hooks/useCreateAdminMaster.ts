import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createAdminMaster } from '../api'
import { adminMastersQueryKey } from './useAdminMasters'

export function useCreateAdminMaster() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createAdminMaster,
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
