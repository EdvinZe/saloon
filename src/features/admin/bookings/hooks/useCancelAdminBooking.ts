import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cancelAdminBooking } from '../api'

export function useCancelAdminBooking() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: cancelAdminBooking,
    onSuccess: response => {
      void queryClient.invalidateQueries({ queryKey: ['admin-bookings'] })
      void queryClient.invalidateQueries({ queryKey: ['admin-booking', response.booking.id] })
      void queryClient.invalidateQueries({ queryKey: ['booking-slots'] })
      void queryClient.invalidateQueries({ queryKey: ['manage-booking-slots'] })
      void queryClient.invalidateQueries({ queryKey: ['available-masters'] })
      void queryClient.invalidateQueries({ queryKey: ['manage-available-masters'] })
    },
  })
}
