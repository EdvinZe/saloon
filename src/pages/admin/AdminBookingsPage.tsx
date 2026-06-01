import { useMemo, useState } from 'react'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import AdminBookingDetailsModal from '../../features/admin/bookings/components/AdminBookingDetailsModal'
import AdminBookingsList from '../../features/admin/bookings/components/AdminBookingsList'
import AdminBookingsToolbar from '../../features/admin/bookings/components/AdminBookingsToolbar'
import AdminCancelBookingModal from '../../features/admin/bookings/components/AdminCancelBookingModal'
import { useAdminBookings } from '../../features/admin/bookings/hooks/useAdminBookings'
import { useCancelAdminBooking } from '../../features/admin/bookings/hooks/useCancelAdminBooking'
import { useCompleteAdminBooking } from '../../features/admin/bookings/hooks/useCompleteAdminBooking'
import { useNoShowAdminBooking } from '../../features/admin/bookings/hooks/useNoShowAdminBooking'
import type { AdminBooking, AdminBookingStatus } from '../../features/admin/bookings/types'
import { useAdminMasters } from '../../features/admin/masters/hooks/useAdminMasters'
import { useAdminServices } from '../../features/admin/services/hooks/useAdminServices'

function getErrorMessage(error: unknown, fallback: string) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'responseBody' in error &&
    typeof error.responseBody === 'object' &&
    error.responseBody !== null &&
    'detail' in error.responseBody &&
    typeof error.responseBody.detail === 'string'
  ) {
    return error.responseBody.detail
  }

  return fallback
}

export default function AdminBookingsPage() {
  const [date, setDate] = useState('')
  const [status, setStatus] = useState<AdminBookingStatus | 'all'>('all')
  const [masterId, setMasterId] = useState<number | 'all'>('all')
  const [serviceId, setServiceId] = useState<number | 'all'>('all')
  const [selectedBooking, setSelectedBooking] = useState<AdminBooking | null>(null)
  const [cancellingBooking, setCancellingBooking] = useState<AdminBooking | null>(null)
  const [submittingBookingId, setSubmittingBookingId] = useState<number | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)

  const bookingParams = useMemo(() => ({
    date: date || null,
    status: status === 'all' ? null : status,
    masterId: masterId === 'all' ? null : masterId,
    serviceId: serviceId === 'all' ? null : serviceId,
  }), [date, masterId, serviceId, status])

  const bookingsQuery = useAdminBookings(bookingParams)
  const mastersQuery = useAdminMasters()
  const servicesQuery = useAdminServices()
  const completeMutation = useCompleteAdminBooking()
  const noShowMutation = useNoShowAdminBooking()
  const cancelMutation = useCancelAdminBooking()

  const clearFilters = () => {
    setDate('')
    setStatus('all')
    setMasterId('all')
    setServiceId('all')
  }

  const completeBooking = (booking: AdminBooking) => {
    setSubmittingBookingId(booking.id)
    setActionMessage(null)
    completeMutation.mutate(booking.id, {
      onSuccess: response => setActionMessage(response.message),
      onSettled: () => setSubmittingBookingId(null),
    })
  }

  const noShowBooking = (booking: AdminBooking) => {
    setSubmittingBookingId(booking.id)
    setActionMessage(null)
    noShowMutation.mutate(booking.id, {
      onSuccess: response => setActionMessage(response.message),
      onSettled: () => setSubmittingBookingId(null),
    })
  }

  const cancelBooking = (booking: AdminBooking) => {
    setSubmittingBookingId(booking.id)
    setActionMessage(null)
    cancelMutation.mutate(booking.id, {
      onSuccess: response => {
        setActionMessage(response.message)
        setCancellingBooking(null)
      },
      onSettled: () => setSubmittingBookingId(null),
    })
  }

  const actionError =
    completeMutation.isError
      ? getErrorMessage(completeMutation.error, 'Failed to complete booking')
      : noShowMutation.isError
        ? getErrorMessage(noShowMutation.error, 'Failed to mark booking no-show')
        : null

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminBookingsToolbar
          date={date}
          status={status}
          masterId={masterId}
          serviceId={serviceId}
          masters={mastersQuery.data ?? []}
          services={servicesQuery.data ?? []}
          onDateChange={setDate}
          onStatusChange={setStatus}
          onMasterChange={setMasterId}
          onServiceChange={setServiceId}
          onClearFilters={clearFilters}
        />

        {actionMessage ? (
          <div className="border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-100">
            {actionMessage}
          </div>
        ) : null}

        {actionError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {actionError}
          </div>
        ) : null}

        {bookingsQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading bookings...
          </div>
        ) : null}

        {bookingsQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(bookingsQuery.error, 'Failed to load bookings')}
          </div>
        ) : null}

        {bookingsQuery.data ? (
          <AdminBookingsList
            bookings={bookingsQuery.data}
            submittingBookingId={submittingBookingId}
            onView={setSelectedBooking}
            onComplete={completeBooking}
            onNoShow={noShowBooking}
            onCancel={booking => {
              cancelMutation.reset()
              setCancellingBooking(booking)
            }}
          />
        ) : null}
      </div>

      {selectedBooking ? (
        <AdminBookingDetailsModal
          booking={selectedBooking}
          onClose={() => setSelectedBooking(null)}
        />
      ) : null}

      {cancellingBooking ? (
        <AdminCancelBookingModal
          booking={cancellingBooking}
          isCancelling={cancelMutation.isPending}
          errorMessage={cancelMutation.isError ? getErrorMessage(cancelMutation.error, 'Failed to cancel booking') : null}
          onClose={() => setCancellingBooking(null)}
          onConfirm={cancelBooking}
        />
      ) : null}
    </AdminLayout>
  )
}
