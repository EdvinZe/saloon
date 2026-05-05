import axios from 'axios'
import type { Master, Service } from '../../shared/data/mockData'
import { MOCK_MASTERS, SERVICES } from '../../shared/data/mockData'
import {
  generateSlotTimes,
  toMinutes,
  WORK_END,
} from './utils/timeSlots'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

// ─── Shared ────────────────────────────────────────────────────────────────────

export interface SlotStatus {
  time: string
  taken: boolean
}

interface MockBusyBooking {
  startTime: string
  durationMin: number
}

const MOCK_BUSY_BOOKINGS: MockBusyBooking[] = [
  { startTime: '09:00', durationMin: 60 },
  { startTime: '10:30', durationMin: 60 },
  { startTime: '13:00', durationMin: 60 },
  { startTime: '15:30', durationMin: 60 },
  { startTime: '17:00', durationMin: 60 },
]

function hasOverlap(
  startA: number,
  endA: number,
  startB: number,
  endB: number
): boolean {
  return startA < endB && endA > startB
}

// ─── New-booking API ────────────────────────────────────────────────────────────

export async function getAvailableSlots(_date: string): Promise<SlotStatus[]> {
  // Replace with: return _api.get(`/slots?date=${_date}`).then(r => r.data)
  return Promise.resolve(
    generateSlotTimes().map(time => ({
      time,
      taken: MOCK_BUSY_BOOKINGS.some(booking => booking.startTime === time),
    }))
  )
}

export async function getAvailableMasters(_date: string, _time: string): Promise<Master[]> {
  // Replace with: return _api.get(`/masters/available?date=${_date}&time=${_time}`).then(r => r.data)
  return Promise.resolve(MOCK_MASTERS)
}

export interface BookingPayload {
  serviceId: string
  date: string
  time: string
  masterId: string
  clientName: string
  clientPhone: string
}

export async function createBooking(data: BookingPayload) {
  return _api.post('/bookings', data).then(r => r.data)
}

// ─── Manage-booking API ─────────────────────────────────────────────────────────

export interface ManagedBooking {
  id: string
  service: Service
  date: string   // 'yyyy-MM-dd'
  time: string   // 'HH:MM'
  master: Master
  depositPaid: number
  status: 'pending' | 'confirmed'
}

export type ManagedSlotStatus = {
  time: string
  status: 'taken' | 'tooShort' | 'free'
}

// Mock overlap data: each entry is a hard booking another client already has
interface MockExistingBooking {
  masterId: string
  date: string
  startTime: string  // 'HH:MM'
  durationMin: number
}

const d = new Date()
const TODAY_STR = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

// Alex busy at 11:00 today — triggers Step 3 (master select) in reschedule flow
// Michael busy at 14:00 today — demonstrates multi-master filtering
const MOCK_EXISTING: MockExistingBooking[] = [
  { masterId: '1', date: TODAY_STR, startTime: '11:00', durationMin: 45 },
  { masterId: '2', date: TODAY_STR, startTime: '14:00', durationMin: 30 },
]

export function isMasterBusyAt(masterId: string, date: string, startTime: string, durationMin: number): boolean {
  const newStart = toMinutes(startTime)
  const newEnd = newStart + durationMin
  return MOCK_EXISTING.some(b => {
    if (b.masterId !== masterId || b.date !== date) return false
    const bStart = toMinutes(b.startTime)
    const bEnd = bStart + b.durationMin
    // Standard overlap: new interval overlaps existing if newStart < bEnd && newEnd > bStart
    return newStart < bEnd && newEnd > bStart
  })
}

export async function getBookingByToken(_token: string): Promise<ManagedBooking> {
  // Replace with: return _api.get(`/api/v1/bookings/manage?token=${_token}`).then(r => r.data)
  return Promise.resolve({
    id: 'BK-001',
    service: SERVICES.find(s => s.id === 'haircut')!,
    date: TODAY_STR,
    time: '09:30',
    master: MOCK_MASTERS[0],  // Alex Kravtsov
    depositPaid: 8,
    status: 'confirmed' as const,
  })
}

export async function getSlotsForService(date: string, serviceId: string): Promise<ManagedSlotStatus[]> {
  // Replace with: return _api.get(`/api/v1/bookings/slots?date=${date}&service_id=${serviceId}`).then(r => r.data)
  void date

  const service = SERVICES.find(s => s.id === serviceId)
  if (!service) return Promise.resolve([])

  const needed = service.durationMin + service.bufferMin
  const endOfDay = toMinutes(WORK_END)
  const times = generateSlotTimes()

  return Promise.resolve(
    times.map(time => {
      const slotStart = toMinutes(time)
      const slotEnd = slotStart + needed

      const exactTaken = MOCK_BUSY_BOOKINGS.some(booking => {
        return toMinutes(booking.startTime) === slotStart
      })

      const overlaps = MOCK_BUSY_BOOKINGS.some(booking => {
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
  )
}

export async function getAvailableMastersForReschedule(
  date: string,
  startTime: string,
  durationMin: number,
): Promise<Master[]> {
  // Replace with: return _api.get(`/api/v1/masters/available?date=${date}&time=${startTime}&duration=${durationMin}`).then(r => r.data)
  return Promise.resolve(
    MOCK_MASTERS.filter(m => !isMasterBusyAt(m.id, date, startTime, durationMin))
  )
}

export interface ReschedulePayload {
  token: string
  serviceId: string
  date: string
  time: string
  masterId: string
}

export async function rescheduleBooking(data: ReschedulePayload): Promise<{ success: boolean }> {
  // Replace with: return _api.post('/api/v1/bookings/reschedule', data).then(r => r.data)
  void data
  return Promise.resolve({ success: true })
}

export async function cancelBooking(token: string): Promise<{ success: boolean }> {
  // Replace with: return _api.post('/api/v1/bookings/cancel', { token }).then(r => r.data)
  void token
  return Promise.resolve({ success: true })
}
