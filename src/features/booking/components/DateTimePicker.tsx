import { useEffect, useState } from 'react'
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  getDay,
  isBefore,
  isToday,
  startOfDay,
  addMonths,
  subMonths,
} from 'date-fns'
import type { Service } from '../../services/api'
import { useAvailableSlots } from '../hooks/useAvailableSlots'
import { useNearestAvailableSlot } from '../hooks/useNearestAvailableSlot'

interface Props {
  service: Service
  selectedDate: string | null
  selectedTime: string | null
  onSelect: (date: string, time: string) => void
}

const TODAY = new Date()

const DAY_HEADERS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

export default function DateTimePicker({ service, selectedDate, selectedTime, onSelect }: Props) {
  const [viewMonth, setViewMonth] = useState(TODAY)
  // pickedDate drives calendar highlight & slot fetch; commits to store only on slot click
  const [pickedDate, setPickedDate] = useState<string | null>(selectedDate)
  const { data: nearestSlot = null } = useNearestAvailableSlot(service.id)
  const { data: slots = [] } = useAvailableSlots(pickedDate, service.id)

  useEffect(() => {
    if (selectedDate === null) {
      const timeoutId = window.setTimeout(() => setPickedDate(null), 0)
      return () => window.clearTimeout(timeoutId)
    }
    // Sync calendar highlight and month view when selectedDate is set externally
    // (e.g. query-param prefill from AI assistant). We only run this when selectedDate
    // changes — intentional omission of pickedDate from deps to avoid fighting manual picks.
    setPickedDate(selectedDate)
    setViewMonth(new Date(selectedDate + 'T12:00:00'))
  }, [selectedDate]) // eslint-disable-line react-hooks/exhaustive-deps

  const days = eachDayOfInterval({ start: startOfMonth(viewMonth), end: endOfMonth(viewMonth) })
  // Monday-first offset: getDay returns 0=Sun…6=Sat, remap to 0=Mon…6=Sun
  const firstDayOffset = (getDay(startOfMonth(viewMonth)) + 6) % 7

  const handleDayClick = (day: Date) => {
    if (isBefore(startOfDay(day), startOfDay(TODAY))) return
    setPickedDate(format(day, 'yyyy-MM-dd'))
  }

  const handleSlotClick = (
    time: string,
    status: 'taken' | 'tooShort' | 'free'
  ) => {
    if (status !== 'free' || !pickedDate) return
    onSelect(pickedDate, time)
  }

  const handleNearest = () => {
    if (!nearestSlot) return
    setPickedDate(nearestSlot.date)
    setViewMonth(new Date(nearestSlot.date + 'T12:00:00'))
    onSelect(nearestSlot.date, nearestSlot.time)
  }

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <div style={{ marginBottom: '28px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
          Step 2
        </p>
        <h2 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400 }}>Pick a date & time</h2>
      </div>

      {/* Nearest available banner — only shown when no date is pre-selected */}
      {nearestSlot && !selectedDate && (
        <div
          onClick={handleNearest}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '14px',
            padding: '14px 20px',
            border: '1px solid #2a2218',
            marginBottom: '24px',
            cursor: 'pointer',
            transition: 'border-color 0.2s',
            background: '#141008',
            boxSizing: 'border-box',
          }}
          onMouseEnter={e => (e.currentTarget.style.borderColor = '#c9a84c')}
          onMouseLeave={e => (e.currentTarget.style.borderColor = '#2a2218')}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0, flexWrap: 'wrap' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#c9a84c', flexShrink: 0 }} />
            <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
              Nearest available:
            </span>
            <span style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'sans-serif' }}>
              {format(new Date(nearestSlot.date + 'T12:00:00'), 'EEE MMM d')} · {nearestSlot.time}
            </span>
          </div>
          <span style={{ fontSize: '16px', color: '#c9a84c', fontFamily: 'Georgia, serif', flexShrink: 0 }}>→</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1px', background: '#2a2218', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
        {/* Calendar */}
        <div style={{ background: '#141008', padding: 'clamp(20px, 5vw, 28px)', minWidth: 0, boxSizing: 'border-box' }}>
          {/* Month navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <button
              onClick={() => setViewMonth(prev => subMonths(prev, 1))}
              style={{ background: 'none', border: 'none', color: '#c9a84c', cursor: 'pointer', fontSize: '18px', padding: '4px 8px', lineHeight: 1 }}
            >
              ←
            </button>
            <span style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'Georgia, serif', letterSpacing: '2px' }}>
              {format(viewMonth, 'MMMM yyyy')}
            </span>
            <button
              onClick={() => setViewMonth(prev => addMonths(prev, 1))}
              style={{ background: 'none', border: 'none', color: '#c9a84c', cursor: 'pointer', fontSize: '18px', padding: '4px 8px', lineHeight: 1 }}
            >
              →
            </button>
          </div>

          {/* Weekday headers */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px', marginBottom: '6px' }}>
            {DAY_HEADERS.map(d => (
              <div key={d} style={{ textAlign: 'center', fontSize: '10px', color: '#3a3020', fontFamily: 'sans-serif', letterSpacing: '1px', padding: '4px 0' }}>
                {d}
              </div>
            ))}
          </div>

          {/* Days */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px' }}>
            {Array.from({ length: firstDayOffset }).map((_, i) => <div key={`pad-${i}`} />)}
            {days.map(day => {
              const isPast = isBefore(startOfDay(day), startOfDay(TODAY))
              const dayStr = format(day, 'yyyy-MM-dd')
              const sel = pickedDate === dayStr
              const tod = isToday(day)

              return (
                <div
                  key={dayStr}
                  onClick={() => handleDayClick(day)}
                  style={{
                    textAlign: 'center',
                    padding: '8px 2px',
                    fontSize: '13px',
                    fontFamily: 'sans-serif',
                    color: isPast ? '#2a2218' : sel ? '#c9a84c' : tod ? '#e8e0d0' : '#7a7060',
                    cursor: isPast ? 'not-allowed' : 'pointer',
                    border: sel ? '1px solid #c9a84c' : '1px solid transparent',
                    background: sel ? 'rgba(201,168,76,0.08)' : 'transparent',
                    transition: 'all 0.15s',
                    borderRadius: '2px',
                    userSelect: 'none',
                  }}
                  onMouseEnter={e => { if (!isPast && !sel) (e.currentTarget as HTMLDivElement).style.color = '#e8e0d0' }}
                  onMouseLeave={e => { if (!isPast && !sel) (e.currentTarget as HTMLDivElement).style.color = tod ? '#e8e0d0' : '#7a7060' }}
                >
                  {format(day, 'd')}
                </div>
              )
            })}
          </div>
        </div>

        {/* Time slots */}
        <div style={{ background: '#141008', padding: 'clamp(20px, 5vw, 28px)', minWidth: 0, boxSizing: 'border-box' }}>
          {!pickedDate ? (
            <div style={{ color: '#3a3020', fontFamily: 'sans-serif', fontSize: '13px', textAlign: 'center', paddingTop: '60px' }}>
              Select a date first
            </div>
          ) : (
            <>
              <div style={{ fontSize: '10px', color: '#7a7060', fontFamily: 'sans-serif', letterSpacing: '3px', textTransform: 'uppercase', marginBottom: '20px' }}>
                {format(new Date(pickedDate + 'T12:00:00'), 'EEEE, MMM d')}
              </div>
              {slots.length === 0 ? (
                <div style={{ color: '#5a5040', fontFamily: 'sans-serif', fontSize: '13px', lineHeight: 1.7, textAlign: 'center', padding: '36px 12px' }}>
                  No available times for this date. Please choose another day.
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(72px, 1fr))', gap: '8px' }}>
                  {slots.map(slot => {
                  const isTaken = slot.status === 'taken'
                  const isTooShort = slot.status === 'tooShort'
                  const isFree = slot.status === 'free'
                  const selSlot = selectedTime === slot.time && selectedDate === pickedDate

                  return (
                    <div
                      key={slot.time}
                      onClick={() => handleSlotClick(slot.time, slot.status)}
                      style={{
                        padding: '10px 14px',
                        fontSize: '13px',
                        fontFamily: 'sans-serif',
                        textAlign: 'center',
                        color: isTaken
                          ? '#2a2218'
                          : selSlot
                            ? '#c9a84c'
                            : isTooShort
                              ? '#3a3020'
                              : '#7a7060',
                        textDecoration: isTaken ? 'line-through' : 'none',
                        border: selSlot ? '1px solid #c9a84c' : '1px solid #2a2218',
                        background: selSlot ? 'rgba(201,168,76,0.06)' : 'transparent',
                        cursor: isFree ? 'pointer' : 'not-allowed',
                        opacity: isTooShort ? 0.4 : 1,
                        transition: 'all 0.15s',
                        userSelect: 'none',
                        boxSizing: 'border-box',
                      }}
                      onMouseEnter={e => {
                        if (isFree && !selSlot) {
                          ;(e.currentTarget as HTMLDivElement).style.borderColor = '#c9a84c'
                        }
                      }}
                      onMouseLeave={e => {
                        if (isFree && !selSlot) {
                          ;(e.currentTarget as HTMLDivElement).style.borderColor = '#2a2218'
                        }
                      }}
                    >
                      {slot.time}
                    </div>
                  )
                  })}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
