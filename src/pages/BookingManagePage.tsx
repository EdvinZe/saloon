import { useState, useEffect, useRef } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import Footer from '../components/layout/Footer'
import {
  getBookingByToken,
  rescheduleManagedBooking,
  cancelManagedBooking,
} from '../features/booking/api'
import { useManageStore } from '../features/bookingmanage/hooks/useManageStore'
import BookingManageHeader from '../features/bookingmanage/components/BookingManageHeader'
import BookingManageDetailsCard from '../features/bookingmanage/components/BookingManageDetailsCard'
import BookingManageActions from '../features/bookingmanage/components/BookingManageActions'
import BookingManageResult from '../features/bookingmanage/components/BookingManageResult'
import BookingManageReschedulePanel from '../features/bookingmanage/components/BookingManageReschedulePanel'
import BookingManageCancelPanel from '../features/bookingmanage/components/BookingManageCancelPanel'

type ActivePanel = 'none' | 'reschedule' | 'cancel'
type DoneType = 'rescheduled' | 'cancelled'

function getErrorStatus(error: unknown): number | null {
  return typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    typeof error.status === 'number'
    ? error.status
    : null
}

function getErrorDetail(error: unknown): string | null {
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

  return null
}

export default function BookingManagePage() {
  const [params] = useSearchParams()
  const token = params.get('token')?.trim() ?? ''
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    newSlot, newMaster, step,
    setNewSlot, setNewMaster, reset,
  } = useManageStore()

  const [activePanel, setActivePanel] = useState<ActivePanel>('none')
  const [doneType, setDoneType] = useState<DoneType | null>(null)
  const [rescheduleSuccess, setRescheduleSuccess] = useState(false)
  const [isRedirectingAfterReschedule, setIsRedirectingAfterReschedule] = useState(false)

  // Step reveal refs
  const rescheduleRef = useRef<HTMLDivElement>(null)
  const cancelRef = useRef<HTMLDivElement>(null)
  const step2Ref = useRef<HTMLDivElement>(null)
  const step3Ref = useRef<HTMLDivElement>(null)
  const confirmRef = useRef<HTMLDivElement>(null)

  const { data: booking, error, isLoading, isError } = useQuery({
    queryKey: ['booking-manage', token],
    queryFn: () => getBookingByToken(token),
    enabled: Boolean(token),
    retry: false,
    staleTime: 5 * 60_000,
  })

  // Reset form state when token changes (page load)
  useEffect(() => { reset() }, [token, reset])

  const needsMasterSelect = Boolean(newSlot)
  const canConfirm = Boolean(newSlot && newMaster)

  // ScrollIntoView when steps advance — mirrors BookingPage pattern
  const prevStep = useRef(step)
  useEffect(() => {
    if (step > prevStep.current) {
      if (step === 2) {
        setTimeout(() => step2Ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
      } else if (step === 3) {
        const target = needsMasterSelect ? step3Ref : confirmRef
        setTimeout(() => target.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
      }
    }
    prevStep.current = step
  }, [step, needsMasterSelect])

  // Also scroll to confirm when needsMasterSelect → false (master step skipped)
  const prevNeedsMaster = useRef(needsMasterSelect)
  useEffect(() => {
    if (prevNeedsMaster.current && !needsMasterSelect && newSlot) {
      setTimeout(() => confirmRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    }
    prevNeedsMaster.current = needsMasterSelect
  }, [needsMasterSelect, newSlot])

  const handlePanelSelect = (panel: 'reschedule' | 'cancel') => {
    const next: ActivePanel = activePanel === panel ? 'none' : panel
    setActivePanel(next)
    setRescheduleSuccess(false)
    setIsRedirectingAfterReschedule(false)
    reset()
    if (next === 'reschedule') {
      setTimeout(() => rescheduleRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    } else if (next === 'cancel') {
      setTimeout(() => cancelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    }
  }

  const rescheduleMutation = useMutation({
    mutationFn: rescheduleManagedBooking,
    onSuccess: response => {
      queryClient.setQueryData(['booking-manage', token], response.booking)
      reset()
      setActivePanel('none')
      setRescheduleSuccess(true)
      setIsRedirectingAfterReschedule(true)
      setTimeout(() => navigate('/'), 1200)
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => cancelManagedBooking(token),
    onSuccess: response => {
      queryClient.setQueryData(['booking-manage', token], response.booking)
      setDoneType('cancelled')
    },
  })

  const handleReschedule = () => {
    if (!canConfirm || !newMaster || !newSlot || isRedirectingAfterReschedule) return
    rescheduleMutation.mutate({
      token,
      master_id: newMaster.id,
      date: newSlot.date,
      time: newSlot.time,
    })
  }

  // ── No token ──────────────────────────────────────────────────────────────────
  if (!token) {
    return (
      <Navigate
        replace
        to="/booking/error?type=booking_manage&reason=missing_token"
      />
    )
  }

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div style={{ background: '#0f0f0f', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#5a5040', fontFamily: 'sans-serif', fontSize: '11px', letterSpacing: '3px', textTransform: 'uppercase' }}>
          Loading...
        </div>
      </div>
    )
  }

  // ── Error / expired token ─────────────────────────────────────────────────────
  if (isError || !booking) {
    const reason = getErrorStatus(error) === 400 ? 'missing_token' : 'invalid_token'

    return (
      <Navigate
        replace
        to={`/booking/error?type=booking_manage&reason=${reason}`}
      />
    )
  }

  if (cancelMutation.isError && getErrorStatus(cancelMutation.error) === 404) {
    return (
      <Navigate
        replace
        to="/booking/error?type=booking_manage&reason=invalid_token"
      />
    )
  }

  if (rescheduleMutation.isError && getErrorStatus(rescheduleMutation.error) === 404) {
    return (
      <Navigate
        replace
        to="/booking/error?type=booking_manage&reason=invalid_token"
      />
    )
  }

  // ── Post-action success screen ────────────────────────────────────────────────
  if (doneType) {
    return (
      <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
        <BookingManageResult doneType={doneType} depositPaid={booking.depositPaid} />
        <Footer />
      </div>
    )
  }

  // ── Main page ─────────────────────────────────────────────────────────────────
  const bookingDateFormatted = format(new Date(booking.date + 'T12:00:00'), 'EEE, MMM d')
  const isBookingCancelled = booking.status === 'cancelled'
  const canManageBooking = booking.status === 'confirmed'
  const cancelErrorMessage =
    cancelMutation.isError && getErrorStatus(cancelMutation.error) === 400
      ? getErrorDetail(cancelMutation.error) ?? 'Booking cannot be cancelled'
      : cancelMutation.isError
        ? 'Could not cancel booking. Please try again.'
        : null
  const rescheduleErrorMessage =
    rescheduleMutation.isError && getErrorStatus(rescheduleMutation.error) === 400
      ? getErrorDetail(rescheduleMutation.error) ?? 'This time is no longer available. Please choose another time.'
      : rescheduleMutation.isError
        ? 'Could not reschedule booking. Please try again.'
        : null

  const bookingRows: { label: string; value: string; gold?: boolean }[] = [
    { label: 'Service',      value: `${booking.service.name} · ${booking.service.totalDurationMinutes} min` },
    { label: 'Date & time',  value: `${bookingDateFormatted} · ${booking.time}` },
    { label: 'Barber',       value: booking.master.name },
    { label: 'Status',       value: isBookingCancelled ? 'Cancelled' : booking.status },
    { label: 'Deposit paid', value: `€${booking.depositPaid}`, gold: true },
  ]

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', overflowX: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'center', padding: '60px clamp(16px, 5vw, 24px) 80px', width: '100%', boxSizing: 'border-box' }}>
        <div style={{ width: '100%', maxWidth: '520px', minWidth: 0, boxSizing: 'border-box' }}>

          <BookingManageHeader />
          <BookingManageDetailsCard rows={bookingRows} />
          {canManageBooking && (
            <BookingManageActions activePanel={activePanel} onSelect={handlePanelSelect} />
          )}

          {isBookingCancelled && (
            <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '20px 24px', marginTop: '12px', color: '#c9a84c', fontFamily: 'Georgia, serif', fontSize: '15px', textAlign: 'center' }}>
              Booking cancelled
            </div>
          )}

          {rescheduleSuccess && (
            <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '20px 24px', marginTop: '12px', color: '#c9a84c', fontFamily: 'Georgia, serif', fontSize: '15px', textAlign: 'center' }}>
              Booking rescheduled successfully
            </div>
          )}

          <BookingManageReschedulePanel
            visible={canManageBooking && activePanel === 'reschedule'}
            panelRef={rescheduleRef}
            step2Ref={step2Ref}
            step3Ref={step3Ref}
            confirmRef={confirmRef}
            service={booking.service}
            newSlot={newSlot}
            newMaster={newMaster}
            depositPaid={booking.depositPaid}
            currentMasterName={booking.master.name}
            needsMasterSelect={needsMasterSelect}
            canConfirm={canConfirm}
            onSlotSelect={setNewSlot}
            onMasterSelect={setNewMaster}
            onConfirm={handleReschedule}
            submitting={rescheduleMutation.isPending || isRedirectingAfterReschedule}
            isError={rescheduleMutation.isError}
            errorMessage={rescheduleErrorMessage}
          />

          <BookingManageCancelPanel
            visible={canManageBooking && activePanel === 'cancel'}
            panelRef={cancelRef}
            depositPaid={booking.depositPaid}
            onConfirm={() => cancelMutation.mutate()}
            onKeep={() => setActivePanel('none')}
            submitting={cancelMutation.isPending}
            isError={cancelMutation.isError}
            errorMessage={cancelErrorMessage}
          />

        </div>
      </div>
      <Footer />
    </div>
  )
}
