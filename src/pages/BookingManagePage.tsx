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
import ManageServiceSelect from '../features/booking/components/ManageServiceSelect'
import ManageTimeSlots from '../features/booking/components/ManageTimeSlots'
import ManageMasterSelect from '../features/booking/components/ManageMasterSelect'
import CancelConfirm from '../features/booking/components/CancelConfirm'

type ActivePanel = 'none' | 'reschedule' | 'cancel'
type DoneType = 'rescheduled' | 'cancelled'

const revealStyle = (visible: boolean): React.CSSProperties => ({
  maxHeight: visible ? '2000px' : '0',
  opacity: visible ? 1 : 0,
  overflow: 'hidden',
  transition: 'max-height 0.6s ease, opacity 0.5s ease',
  scrollMarginTop: '24px',
})

const ROW: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  padding: '10px 0',
}

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
    const cancelled = doneType === 'cancelled'
    return (
      <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '80px 24px', minHeight: 'calc(100vh - 70px)',
        }}>
          <div style={{ width: '100%', maxWidth: '520px', textAlign: 'center' }}>
            <div style={{
              width: '72px', height: '72px', borderRadius: '50%',
              border: `1px solid ${cancelled ? '#c87070' : '#c9a84c'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 32px', fontSize: '26px',
              color: cancelled ? '#c87070' : '#c9a84c',
              background: cancelled ? 'rgba(200,112,112,0.05)' : 'rgba(201,168,76,0.05)',
            }}>
              {cancelled ? '✕' : '✓'}
            </div>
            <h1 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif', marginBottom: '10px' }}>
              {cancelled ? 'Booking cancelled' : 'Booking rescheduled'}
            </h1>
            <p style={{ fontSize: '12px', color: '#7a7060', fontFamily: 'sans-serif', lineHeight: 1.8 }}>
              {cancelled
                ? `Your deposit of €${booking.depositPaid} will be refunded within 3–5 business days.`
                : 'Your appointment has been updated. A confirmation will be sent shortly.'}
            </p>
          </div>
        </div>
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

          {/* Page header */}
          <div style={{ marginBottom: '36px' }}>
            <p style={{
              fontSize: '10px', letterSpacing: '4px', color: '#c9a84c',
              textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px',
            }}>
              Manage booking
            </p>
            <h1 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif' }}>
              Your appointment
            </h1>
          </div>

          {/* Booking details card */}
          <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px 28px', marginBottom: '20px' }}>
            {bookingRows.map((row, i) => (
              <div key={row.label} style={{ ...ROW, borderBottom: i < bookingRows.length - 1 ? '1px solid #1a1810' : 'none' }}>
                <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
                  {row.label}
                </span>
                <span style={{ fontSize: '13px', color: row.gold ? '#c9a84c' : '#e8e0d0', fontFamily: 'sans-serif' }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>

          {/* Action selector cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '4px' }}>

            {/* Reschedule */}
            <div
              onClick={() => handlePanelSelect('reschedule')}
              style={{
                background: activePanel === 'reschedule' ? 'rgba(201,168,76,0.05)' : '#141008',
                border: activePanel === 'reschedule' ? '1px solid #c9a84c' : '1px solid #2a2218',
                padding: '20px',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { if (activePanel !== 'reschedule') (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
              onMouseLeave={e => { if (activePanel !== 'reschedule') (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
            >
              <div style={{ fontSize: '22px', color: '#c9a84c', marginBottom: '8px' }}>↺</div>
              <div style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'Georgia, serif', marginBottom: '4px' }}>Reschedule</div>
              <div style={{ fontSize: '10px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
                Change date, time or service
              </div>
            </div>

            {/* Cancel */}
            <div
              onClick={() => handlePanelSelect('cancel')}
              style={{
                background: activePanel === 'cancel' ? 'rgba(200,112,112,0.05)' : '#141008',
                border: activePanel === 'cancel' ? '1px solid #c87070' : '1px solid #2a2218',
                padding: '20px',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { if (activePanel !== 'cancel') (e.currentTarget as HTMLDivElement).style.borderColor = '#c87070' }}
              onMouseLeave={e => { if (activePanel !== 'cancel') (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
            >
              <div style={{ fontSize: '22px', color: '#c87070', marginBottom: '8px' }}>✕</div>
              <div style={{ fontSize: '13px', color: '#c87070', fontFamily: 'Georgia, serif', marginBottom: '4px' }}>Cancel booking</div>
              <div style={{ fontSize: '10px', color: '#7a5050', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
                Deposit fully refunded
              </div>
            </div>
          </div>

          {/* ── Reschedule panel ──────────────────────────────────────────────── */}
          <div style={revealStyle(activePanel === 'reschedule')}>
            <div
              ref={rescheduleRef}
              style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px', marginTop: '12px' }}
            >
              {/* Step 1 — Service */}
              <ManageServiceSelect selected={newService} onSelect={setNewService} />

              {/* Step 2 — Time (reveals after service selected) */}
              <div ref={step2Ref} style={revealStyle(!!newService)}>
                {newService && (
                  <ManageTimeSlots
                    service={newService}
                    depositPaid={booking.depositPaid}
                    selectedDate={newSlot?.date ?? null}
                    selectedTime={newSlot?.time ?? null}
                    onSelect={setNewSlot}
                  />
                )}
              </div>

              {/* Step 3 — Master (reveals only if current barber unavailable) */}
              <div ref={step3Ref} style={revealStyle(needsMasterSelect)}>
                {needsMasterSelect && newService && newSlot && (
                  <ManageMasterSelect
                    currentMasterName={booking.master.name}
                    service={newService}
                    date={newSlot.date}
                    time={newSlot.time}
                    selected={newMaster}
                    onSelect={setNewMaster}
                  />
                )}
              </div>

              {/* Confirm reschedule (reveals when all required fields are filled) */}
              <div ref={confirmRef} style={revealStyle(canConfirm)}>
                <div style={{ paddingTop: '20px', borderTop: '1px solid #1a1810', marginTop: '4px' }}>
                  <button
                    onClick={handleReschedule}
                    disabled={rescheduleMutation.isPending}
                    style={{
                      width: '100%',
                      padding: '14px',
                      background: 'transparent',
                      border: '1px solid #c9a84c',
                      color: '#c9a84c',
                      fontSize: '11px',
                      letterSpacing: '3px',
                      textTransform: 'uppercase',
                      fontFamily: 'Georgia, serif',
                      cursor: rescheduleMutation.isPending ? 'not-allowed' : 'pointer',
                      opacity: rescheduleMutation.isPending ? 0.5 : 1,
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={e => { if (!rescheduleMutation.isPending) e.currentTarget.style.background = 'rgba(201,168,76,0.08)' }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
                  >
                    {rescheduleMutation.isPending ? 'Rescheduling...' : 'Confirm reschedule'}
                  </button>

                  {rescheduleMutation.isError && (
                    <div style={{ marginTop: '10px', fontSize: '11px', color: '#c87070', fontFamily: 'sans-serif', textAlign: 'center' }}>
                      Something went wrong. Please try again.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* ── Cancel panel ──────────────────────────────────────────────────── */}
          <div style={revealStyle(activePanel === 'cancel')}>
            <div
              ref={cancelRef}
              style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px', marginTop: '12px' }}
            >
              <CancelConfirm
                depositPaid={booking.depositPaid}
                onConfirm={() => cancelMutation.mutate()}
                onKeep={() => setActivePanel('none')}
                submitting={cancelMutation.isPending}
              />

              {cancelMutation.isError && (
                <div style={{ marginTop: '10px', fontSize: '11px', color: '#c87070', fontFamily: 'sans-serif', textAlign: 'center' }}>
                  Something went wrong. Please try again.
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
      <Footer />
    </div>
  )
}
