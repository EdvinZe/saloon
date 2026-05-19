import type { Service } from '../../services/api'
import type { MockBusyBooking, MockExistingBooking } from '../mock/bookingMockData'
import {
  generateSlotTimes,
  toMinutes,
  WORK_END,
} from './timeSlots'

export type AvailabilitySlotStatus = {
  time: string
  status: 'taken' | 'tooShort' | 'free'
}

export function hasOverlap(
  startA: number,
  endA: number,
  startB: number,
  endB: number
): boolean {
  return startA < endB && endA > startB
}

export function isMasterBusyAt(
  bookings: MockExistingBooking[],
  masterId: string,
  date: string,
  startTime: string,
  durationMin: number
): boolean {
  const newStart = toMinutes(startTime)
  const newEnd = newStart + durationMin
  return bookings.some(b => {
    if (b.masterId !== masterId || b.date !== date) return false
    const bStart = toMinutes(b.startTime)
    const bEnd = bStart + b.durationMin
    // Standard overlap: new interval overlaps existing if newStart < bEnd && newEnd > bStart
    return newStart < bEnd && newEnd > bStart
  })
}

export function getSlotStatusesForService(
  service: Service,
  busyBookings: MockBusyBooking[],
): AvailabilitySlotStatus[] {
  const needed = service.totalDurationMinutes
  const endOfDay = toMinutes(WORK_END)
  const times = generateSlotTimes()

  return times.map(time => {
    const slotStart = toMinutes(time)
    const slotEnd = slotStart + needed

    const exactTaken = busyBookings.some(booking => {
      return toMinutes(booking.startTime) === slotStart
    })

    const overlaps = busyBookings.some(booking => {
      const bookingStart = toMinutes(booking.startTime)
      const bookingEnd = bookingStart + booking.durationMin

      return hasOverlap(slotStart, slotEnd, bookingStart, bookingEnd)
    })

    if (exactTaken) {
      return { time, status: 'taken' as const }
    }

    if (overlaps || slotEnd > endOfDay) {
      return { time, status: 'tooShort' as const }
    }

    return { time, status: 'free' as const }
  })
}
