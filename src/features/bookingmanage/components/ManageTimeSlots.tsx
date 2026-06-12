import { useState, useEffect, useRef } from 'react'
import { format, addDays, startOfDay } from 'date-fns'
import type { Service } from '../../services/api'
import { useManageAvailableSlots } from '../hooks/useManageAvailableSlots'

interface Props {
  service: Service
  selectedDate: string | null
  selectedTime: string | null
  onSelect: (date: string, time: string) => void
  disabled?: boolean
}

export default function ManageTimeSlots({ service, selectedDate, selectedTime, onSelect, disabled = false }: Props) {
  const today = startOfDay(new Date())
  const days = Array.from({ length: 7 }, (_, i) => addDays(today, i))
  const [pickedDate, setPickedDate] = useState(() => format(today, 'yyyy-MM-dd'))

  const { data: slots = [], isLoading } = useManageAvailableSlots(pickedDate, service.id)

  // Scroll slots into view when pickedDate changes and slots load
  const slotsRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!isLoading && slots.length > 0 && slotsRef.current) {
      setTimeout(() => slotsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 120)
    }
  }, [pickedDate, isLoading, slots.length])

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <style>
        {`
          .manage-date-carousel {
            scrollbar-width: none;
            -ms-overflow-style: none;
            -webkit-overflow-scrolling: touch;
          }

          .manage-date-carousel::-webkit-scrollbar {
            display: none;
          }
        `}
      </style>

      <p style={{
        fontSize: '10px', letterSpacing: '3px', color: '#c9a84c',
        textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px',
      }}>
        Step 2 — Time
      </p>

      {/* Date picker row — 7 days forward */}
      <div
        className="manage-date-carousel"
        style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '16px',
          overflowX: 'auto',
          overflowY: 'hidden',
          paddingBottom: '2px',
          width: '100%',
          maxWidth: '100%',
          boxSizing: 'border-box',
          touchAction: 'pan-x',
          overscrollBehaviorX: 'contain',
        }}
      >
        {days.map(day => {
          const ds = format(day, 'yyyy-MM-dd')
          const sel = pickedDate === ds
          return (
            <div
              key={ds}
              onClick={() => { if (!disabled) setPickedDate(ds) }}
              style={{
                flex: '0 0 auto',
                minWidth: '62px',
                padding: '9px 8px',
                textAlign: 'center',
                cursor: disabled ? 'not-allowed' : 'pointer',
                border: sel ? '1px solid #c9a84c' : '1px solid #2a2218',
                background: sel ? 'rgba(201,168,76,0.06)' : '#0f0f0f',
                transition: 'all 0.15s',
                userSelect: 'none',
                boxSizing: 'border-box',
              }}
              onMouseEnter={e => { if (!disabled && !sel) (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
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
        ) : slots.length === 0 ? (
          <div style={{ fontSize: '12px', color: '#5a5040', fontFamily: 'sans-serif', lineHeight: 1.6, padding: '12px 0 18px' }}>
            No available times for this date. Please choose another day.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(64px, 1fr))', gap: '6px', marginBottom: '16px', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
            {slots.map(slot => {
              const isTaken = slot.status === 'taken'
              const isTooShort = slot.status === 'tooShort'
              const isFree = slot.status === 'free'
              const isSelected = selectedDate === pickedDate && selectedTime === slot.time

              return (
                <div
                  key={slot.time}
                  onClick={() => { if (!disabled && isFree) onSelect(pickedDate, slot.time) }}
                  style={{
                    padding: '8px 6px',
                    textAlign: 'center',
                    fontSize: '12px',
                    fontFamily: 'sans-serif',
                    color: isTaken ? '#2a2218' : isSelected ? '#c9a84c' : isTooShort ? '#3a3020' : '#7a7060',
                    textDecoration: isTaken ? 'line-through' : 'none',
                    border: isSelected ? '1px solid #c9a84c' : '1px solid #2a2218',
                    background: isSelected ? 'rgba(201,168,76,0.06)' : 'transparent',
                    cursor: !disabled && isFree ? 'pointer' : 'not-allowed',
                    opacity: disabled ? 0.5 : isTooShort ? 0.4 : 1,
                    transition: 'all 0.15s',
                    userSelect: 'none',
                    boxSizing: 'border-box',
                  }}
                  onMouseEnter={e => { if (!disabled && isFree && !isSelected) (e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c' }}
                  onMouseLeave={e => { if (isFree && !isSelected) (e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218' }}
                >
                  {slot.time}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
