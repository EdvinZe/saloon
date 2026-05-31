import type { CSSProperties, RefObject } from 'react'
import type { Master } from '../../masters/api'
import type { Service } from '../../services/api'
import ManageTimeSlots from './ManageTimeSlots'
import ManageMasterSelect from './ManageMasterSelect'

const revealStyle = (visible: boolean): CSSProperties => ({
  maxHeight: visible ? '2000px' : '0',
  opacity: visible ? 1 : 0,
  overflow: 'hidden',
  transition: 'max-height 0.6s ease, opacity 0.5s ease',
  scrollMarginTop: '24px',
})

interface Props {
  visible: boolean
  panelRef: RefObject<HTMLDivElement | null>
  step2Ref: RefObject<HTMLDivElement | null>
  step3Ref: RefObject<HTMLDivElement | null>
  confirmRef: RefObject<HTMLDivElement | null>
  service: Service
  newSlot: { date: string; time: string } | null
  newMaster: Master | null
  needsMasterSelect: boolean
  canConfirm: boolean
  onSlotSelect: (date: string, time: string) => void
  onMasterSelect: (master: Master | null) => void
  onConfirm: () => void
  submitting: boolean
  isError: boolean
  errorMessage?: string | null
}

export default function BookingManageReschedulePanel({
  visible,
  panelRef,
  step2Ref,
  step3Ref,
  confirmRef,
  service,
  newSlot,
  newMaster,
  needsMasterSelect,
  canConfirm,
  onSlotSelect,
  onMasterSelect,
  onConfirm,
  submitting,
  isError,
  errorMessage,
}: Props) {
  const disabled = submitting || !canConfirm

  return (
    <div style={revealStyle(visible)}>
      <div
        ref={panelRef}
        style={{ background: '#141008', border: '1px solid #2a2218', padding: 'clamp(20px, 6vw, 24px)', marginTop: '12px', width: '100%', boxSizing: 'border-box', minWidth: 0 }}
      >
        <div style={{ width: '100%', minWidth: 0 }}>
          <p style={{
            fontSize: '10px', letterSpacing: '3px', color: '#c9a84c',
            textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px',
          }}>
            Booked service
          </p>
          <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(201,168,76,0.16)', padding: '18px 20px', marginBottom: '28px', boxSizing: 'border-box', cursor: 'default' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '14px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '16px', color: '#e8e0d0', fontFamily: 'Georgia, serif', fontWeight: 500 }}>
                {service.name}
              </span>
              <span style={{ color: '#b89a4a', border: '1px solid rgba(201,168,76,0.16)', padding: '4px 8px', borderRadius: '999px', fontFamily: 'sans-serif', fontSize: '12px', letterSpacing: '1px', lineHeight: 1 }}>
                {service.totalDurationMinutes} min
              </span>
            </div>
            <div style={{ marginTop: '10px', color: '#5a5040', fontFamily: 'sans-serif', fontSize: '11px', lineHeight: 1.5 }}>
              Service cannot be changed for this booking.
            </div>
          </div>
        </div>

        <div ref={step2Ref} style={revealStyle(true)}>
          <ManageTimeSlots
            service={service}
            selectedDate={newSlot?.date ?? null}
            selectedTime={newSlot?.time ?? null}
            onSelect={onSlotSelect}
            disabled={submitting}
          />
        </div>

        {/* Step 3 — Master */}
        <div ref={step3Ref} style={revealStyle(needsMasterSelect)}>
          {needsMasterSelect && newSlot && (
            <ManageMasterSelect
              service={service}
              date={newSlot.date}
              time={newSlot.time}
              selected={newMaster}
              onSelect={onMasterSelect}
              disabled={submitting}
            />
          )}
        </div>

        {/* Confirm reschedule (reveals when all required fields are filled) */}
        <div ref={confirmRef} style={revealStyle(canConfirm)}>
          <div style={{ paddingTop: '20px', borderTop: '1px solid #1a1810', marginTop: '4px', minWidth: 0 }}>
            <div style={{ marginBottom: '12px', color: '#5a5040', fontFamily: 'sans-serif', fontSize: '11px', lineHeight: 1.5, textAlign: 'center' }}>
              No extra payment is required for rescheduling.
            </div>

            <button
              onClick={onConfirm}
              disabled={disabled}
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
                cursor: disabled ? 'not-allowed' : 'pointer',
                opacity: disabled ? 0.5 : 1,
                transition: 'all 0.2s',
                boxSizing: 'border-box',
              }}
              onMouseEnter={e => { if (!disabled) e.currentTarget.style.background = 'rgba(201,168,76,0.08)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
            >
              {submitting ? 'Rescheduling...' : 'Confirm reschedule'}
            </button>

            {isError && (
              <div style={{ marginTop: '10px', fontSize: '11px', color: '#c87070', fontFamily: 'sans-serif', textAlign: 'center' }}>
                {errorMessage ?? 'Could not reschedule booking. Please try again.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
