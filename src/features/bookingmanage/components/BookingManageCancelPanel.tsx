import type { CSSProperties, RefObject } from 'react'
import CancelConfirm from './CancelConfirm'

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
  depositPaid: number
  depositStatus: string
  onConfirm: () => void
  onKeep: () => void
  submitting: boolean
  isError: boolean
  errorMessage?: string | null
}

export default function BookingManageCancelPanel({
  visible,
  panelRef,
  depositPaid,
  depositStatus,
  onConfirm,
  onKeep,
  submitting,
  isError,
  errorMessage,
}: Props) {
  return (
    <div style={revealStyle(visible)}>
      <div
        ref={panelRef}
        style={{ background: '#141008', border: '1px solid #2a2218', padding: 'clamp(20px, 6vw, 24px)', marginTop: '12px', width: '100%', boxSizing: 'border-box', minWidth: 0 }}
      >
        <CancelConfirm
          depositPaid={depositPaid}
          depositStatus={depositStatus}
          onConfirm={onConfirm}
          onKeep={onKeep}
          submitting={submitting}
        />

        {isError && (
          <div style={{ marginTop: '10px', fontSize: '11px', color: '#c87070', fontFamily: 'sans-serif', textAlign: 'center' }}>
            {errorMessage ?? 'Could not cancel booking. Please try again.'}
          </div>
        )}
      </div>
    </div>
  )
}
