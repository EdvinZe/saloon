import { useMutation, useQueryClient } from '@tanstack/react-query'
import { completeAdminBooking } from '../api'

export function useCompleteAdminBooking() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: completeAdminBooking,
    onSuccess: response => {
      void queryClient.invalidateQueries({ queryKey: ['admin-bookings'] })
      void queryClient.invalidateQueries({ queryKey: ['admin-booking', response.booking.id] })
    },
  })
}
