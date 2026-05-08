import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { format } from 'date-fns'
import Footer from '../components/layout/Footer'
import {
  getBookingByToken,
  rescheduleBooking,
  cancelBooking,
  isMasterBusyAt,
} from '../features/booking/api'
import { useManageStore } from '../features/booking/hooks/useManageStore'
import BookingManageHeader from '../features/bookingmanage/components/BookingManageHeader'
import BookingManageDetailsCard from '../features/bookingmanage/components/BookingManageDetailsCard'
import BookingManageActions from '../features/bookingmanage/components/BookingManageActions'
import BookingManageResult from '../features/bookingmanage/components/BookingManageResult'
import BookingManageReschedulePanel from '../features/bookingmanage/components/BookingManageReschedulePanel'
import BookingManageCancelPanel from '../features/bookingmanage/components/BookingManageCancelPanel'

type ActivePanel = 'none' | 'reschedule' | 'cancel'
type DoneType = 'rescheduled' | 'cancelled'

export default function BookingManagePage() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''

  const {
    newService, newSlot, newMaster, step,
    setNewService, setNewSlot, setNewMaster, reset,
  } = useManageStore()

  const [activePanel, setActivePanel] = useState<ActivePanel>('none')
  const [doneType, setDoneType] = useState<DoneType | null>(null)

  // Step reveal refs
  const rescheduleRef = useRef<HTMLDivElement>(null)
  const cancelRef = useRef<HTMLDivElement>(null)
  const step2Ref = useRef<HTMLDivElement>(null)
  const step3Ref = useRef<HTMLDivElement>(null)
  const confirmRef = useRef<HTMLDivElement>(null)

  const { data: booking, isLoading, isError } = useQuery({
    queryKey: ['booking-manage', token],
    queryFn: () => getBookingByToken(token),
    enabled: !!token,
    retry: false,
    staleTime: 5 * 60_000,
  })

  // Reset form state when token changes (page load)
  useEffect(() => { reset() }, [token, reset])

  // Derived: does current barber overlap the newly selected slot?
  const needsMasterSelect = !!(
    newService && newSlot && booking &&
    isMasterBusyAt(booking.master.id, newSlot.date, newSlot.time, newService.durationMin)
  )

  const canConfirm = !!(newService && newSlot && (!needsMasterSelect || newMaster))

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
    reset()
    if (next === 'reschedule') {
      setTimeout(() => rescheduleRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    } else if (next === 'cancel') {
      setTimeout(() => cancelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
    }
  }

  const rescheduleMutation = useMutation({
    mutationFn: rescheduleBooking,
    onSuccess: () => setDoneType('rescheduled'),
  })

  const cancelMutation = useMutation({
    mutationFn: () => cancelBooking(token),
    onSuccess: () => setDoneType('cancelled'),
  })

  const handleReschedule = () => {
    if (!canConfirm || !booking || !newService || !newSlot) return
    const masterId = needsMasterSelect ? (newMaster?.id ?? booking.master.id) : booking.master.id
    rescheduleMutation.mutate({
      token,
      serviceId: newService.id,
      date: newSlot.date,
      time: newSlot.time,
      masterId,
    })
  }

  // ── No token ──────────────────────────────────────────────────────────────────
  if (!token) {
    return (
      <div style={{ background: '#0f0f0f', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#5a5040', fontFamily: 'sans-serif', fontSize: '13px' }}>
          Invalid or missing booking link.
        </div>
      </div>
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
    return (
      <div style={{ background: '#0f0f0f', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#c87070', fontFamily: 'sans-serif', fontSize: '13px' }}>
          Booking not found or this link has expired.
        </div>
      </div>
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

  const bookingRows: { label: string; value: string; gold?: boolean }[] = [
    { label: 'Service',      value: `${booking.service.name} · ${booking.service.dur}` },
    { label: 'Date & time',  value: `${bookingDateFormatted} · ${booking.time}` },
    { label: 'Barber',       value: booking.master.name },
    { label: 'Deposit paid', value: `€${booking.depositPaid}`, gold: true },
  ]

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 24px 80px' }}>
        <div style={{ width: '100%', maxWidth: '520px' }}>

          <BookingManageHeader />
          <BookingManageDetailsCard rows={bookingRows} />
          <BookingManageActions activePanel={activePanel} onSelect={handlePanelSelect} />

          <BookingManageReschedulePanel
            visible={activePanel === 'reschedule'}
            panelRef={rescheduleRef}
            step2Ref={step2Ref}
            step3Ref={step3Ref}
            confirmRef={confirmRef}
            newService={newService}
            newSlot={newSlot}
            newMaster={newMaster}
            depositPaid={booking.depositPaid}
            currentMasterName={booking.master.name}
            needsMasterSelect={needsMasterSelect}
            canConfirm={canConfirm}
            onServiceSelect={setNewService}
            onSlotSelect={setNewSlot}
            onMasterSelect={setNewMaster}
            onConfirm={handleReschedule}
            submitting={rescheduleMutation.isPending}
            isError={rescheduleMutation.isError}
          />

          <BookingManageCancelPanel
            visible={activePanel === 'cancel'}
            panelRef={cancelRef}
            depositPaid={booking.depositPaid}
            onConfirm={() => cancelMutation.mutate()}
            onKeep={() => setActivePanel('none')}
            submitting={cancelMutation.isPending}
            isError={cancelMutation.isError}
          />

        </div>
      </div>
      <Footer />
    </div>
  )
}
