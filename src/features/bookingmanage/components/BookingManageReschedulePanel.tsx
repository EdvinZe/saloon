import type { CSSProperties, RefObject } from 'react'
import type { Service, Master } from '../../../shared/data/mockData'
import ManageServiceSelect from './ManageServiceSelect'
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
  newService: Service | null
  newSlot: { date: string; time: string } | null
  newMaster: Master | null
  depositPaid: number
  currentMasterName: string
  needsMasterSelect: boolean
  canConfirm: boolean
  onServiceSelect: (service: Service) => void
  onSlotSelect: (date: string, time: string) => void
  onMasterSelect: (master: Master) => void
  onConfirm: () => void
  submitting: boolean
  isError: boolean
}

export default function BookingManageReschedulePanel({
  visible,
  panelRef,
  step2Ref,
  step3Ref,
  confirmRef,
  newService,
  newSlot,
  newMaster,
  depositPaid,
  currentMasterName,
  needsMasterSelect,
  canConfirm,
  onServiceSelect,
  onSlotSelect,
  onMasterSelect,
  onConfirm,
  submitting,
  isError,
}: Props) {
  return (
    <div style={revealStyle(visible)}>
      <div
        ref={panelRef}
        style={{ background: '#141008', border: '1px solid #2a2218', padding: 'clamp(20px, 6vw, 24px)', marginTop: '12px', width: '100%', boxSizing: 'border-box', minWidth: 0 }}
      >
        {/* Step 1 — Service */}
        <ManageServiceSelect selected={newService} onSelect={onServiceSelect} />

        {/* Step 2 — Time (reveals after service selected) */}
        <div ref={step2Ref} style={revealStyle(!!newService)}>
          {newService && (
            <ManageTimeSlots
              service={newService}
              depositPaid={depositPaid}
              selectedDate={newSlot?.date ?? null}
              selectedTime={newSlot?.time ?? null}
              onSelect={onSlotSelect}
            />
          )}
        </div>

        {/* Step 3 — Master (reveals only if current barber unavailable) */}
        <div ref={step3Ref} style={revealStyle(needsMasterSelect)}>
          {needsMasterSelect && newService && newSlot && (
            <ManageMasterSelect
              currentMasterName={currentMasterName}
              service={newService}
              date={newSlot.date}
              time={newSlot.time}
              selected={newMaster}
              onSelect={onMasterSelect}
            />
          )}
        </div>

        {/* Confirm reschedule (reveals when all required fields are filled) */}
        <div ref={confirmRef} style={revealStyle(canConfirm)}>
          <div style={{ paddingTop: '20px', borderTop: '1px solid #1a1810', marginTop: '4px', minWidth: 0 }}>
            <button
              onClick={onConfirm}
              disabled={submitting}
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
                cursor: submitting ? 'not-allowed' : 'pointer',
                opacity: submitting ? 0.5 : 1,
                transition: 'all 0.2s',
                boxSizing: 'border-box',
              }}
              onMouseEnter={e => { if (!submitting) e.currentTarget.style.background = 'rgba(201,168,76,0.08)' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
            >
              {submitting ? 'Rescheduling...' : 'Confirm reschedule'}
            </button>

            {isError && (
              <div style={{ marginTop: '10px', fontSize: '11px', color: '#c87070', fontFamily: 'sans-serif', textAlign: 'center' }}>
                Something went wrong. Please try again.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
