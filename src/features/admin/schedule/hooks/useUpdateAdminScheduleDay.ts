import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminScheduleDay } from '../api'

export function useUpdateAdminScheduleDay() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateAdminScheduleDay,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin-schedule'] })
    },
  })
}
