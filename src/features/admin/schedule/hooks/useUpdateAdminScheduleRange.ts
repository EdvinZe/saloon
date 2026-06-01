import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminScheduleRange } from '../api'

export function useUpdateAdminScheduleRange() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateAdminScheduleRange,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin-schedule'] })
    },
  })
}
