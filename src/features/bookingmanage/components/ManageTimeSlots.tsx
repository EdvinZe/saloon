import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format, addDays, startOfDay } from 'date-fns'
import { getSlotsForService } from '../../booking/api'
import type { Service } from '../../../shared/data/mockData'

const SERVICE_DEPOSITS: Record<string, number> = { haircut: 10, beard: 8, combo: 15 }

interface Props {
  service: Service
  depositPaid: number
  selectedDate: string | null
  selectedTime: string | null
  onSelect: (date: string, time: string) => void
}

export default function ManageTimeSlots({ service, depositPaid, selectedDate, selectedTime, onSelect }: Props) {
  const today = startOfDay(new Date())
  const days = Array.from({ length: 7 }, (_, i) => addDays(today, i))
  const [pickedDate, setPickedDate] = useState(() => format(today, 'yyyy-MM-dd'))

  const { data: slots = [], isLoading } = useQuery({
    queryKey: ['manage-slots', pickedDate, service.id],
    queryFn: () => getSlotsForService(pickedDate, service.id),
    staleTime: 60_000,
  })

  // Scroll slots into view when pickedDate changes and slots load
  const slotsRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!isLoading && slots.length > 0 && slotsRef.current) {
      setTimeout(() => slotsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 120)
    }
  }, [pickedDate, isLoading, slots.length])

  const newDep = SERVICE_DEPOSITS[service.id] ?? 0
  const depDiff = newDep - depositPaid
  const slotSelected = !!(selectedDate === pickedDate && selectedTime)

  return (
    <div>
      <p style={{
        fontSize: '10px', letterSpacing: '3px', color: '#c9a84c',
        textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px',
      }}>
        Step 2 — Time
      </p>

      {/* Date picker row — 7 days forward */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px', overflowX: 'auto', paddingBottom: '4px' }}>
        {days.map(day => {
          const ds = format(day, 'yyyy-MM-dd')
          const sel = pickedDate === ds
          return (
            <div
              key={ds}
              onClick={() => setPickedDate(ds)}
              style={{
                flexShrink: 0,
                minWidth: '54px',
                padding: '8px 6px',
                textAlign: 'center',
                cursor: 'pointer',
                border: sel ? '1px solid #c9a84c' : '1px solid #2a2218',
                background: sel ? 'rgba(201,168,76,0.06)' : '#0f0f0f',
                transition: 'all 0.15s',
                userSelect: 'none',
              }}
              onMouseEnter={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
              onMouseLeave={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
            >
              <div style={{ fontSize: '9px', color: '#7a7060', fontFamily: 'sans-serif', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>
                {format(day, 'EEE')}
              </div>
              <div style={{ fontSize: '14px', color: sel ? '#c9a84c' : '#e8e0d0', fontFamily: 'sans-serif' }}>
                {format(day, 'd')}
              </div>
            </div>
          )
        })}
      </div>

      {/* Slot grid */}
      <div ref={slotsRef}>
        {isLoading ? (
          <div style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '2px', padding: '12px 0' }}>
            Loading slots...
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', marginBottom: '16px' }}>
            {slots.map(slot => {
              const isTaken = slot.status === 'taken'
              const isTooShort = slot.status === 'tooShort'
              const isFree = slot.status === 'free'
              const isSelected = selectedDate === pickedDate && selectedTime === slot.time

              return (
                <div
                  key={slot.time}
                  onClick={() => { if (isFree) onSelect(pickedDate, slot.time) }}
                  style={{
                    padding: '8px 6px',
                    textAlign: 'center',
                    fontSize: '12px',
                    fontFamily: 'sans-serif',
                    color: isTaken ? '#2a2218' : isSelected ? '#c9a84c' : isTooShort ? '#3a3020' : '#7a7060',
                    textDecoration: isTaken ? 'line-through' : 'none',
                    border: isSelected ? '1px solid #c9a84c' : '1px solid #2a2218',
                    background: isSelected ? 'rgba(201,168,76,0.06)' : 'transparent',
                    cursor: isFree ? 'pointer' : 'not-allowed',
                    opacity: isTooShort ? 0.4 : 1,
                    transition: 'all 0.15s',
                    userSelect: 'none',
                  }}
                  onMouseEnter={e => { if (isFree && !isSelected) (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
                  onMouseLeave={e => { if (isFree && !isSelected) (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
                >
                  {slot.time}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Deposit diff note — only when a slot on the current date is selected */}
      {slotSelected && (
        <div style={{
          padding: '10px 14px',
          background: '#141008',
          border: `1px solid ${depDiff === 0 ? '#2a2218' : depDiff > 0 ? '#3a2a18' : '#1a3020'}`,
          fontSize: '12px',
          fontFamily: 'sans-serif',
          color: depDiff === 0 ? '#7a7060' : depDiff > 0 ? '#8a6040' : '#5a8060',
          lineHeight: 1.6,
        }}>
          {depDiff === 0
            ? 'Your deposit remains — no extra charge'
            : depDiff > 0
              ? `Extra €${depDiff} deposit required — you will be charged the difference`
              : `€${Math.abs(depDiff)} will be refunded to your card`}
        </div>
      )}
    </div>
  )
}
