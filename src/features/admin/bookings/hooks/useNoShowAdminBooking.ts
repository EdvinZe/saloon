import { useMutation, useQueryClient } from '@tanstack/react-query'
import { noShowAdminBooking } from '../api'

export function useNoShowAdminBooking() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: noShowAdminBooking,
    onSuccess: response => {
      void queryClient.invalidateQueries({ queryKey: ['admin-bookings'] })
      void queryClient.invalidateQueries({ queryKey: ['admin-booking', response.booking.id] })
    },
  })
}
