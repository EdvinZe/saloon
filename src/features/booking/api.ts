import axios from 'axios'
import type { Master, Service } from '../../shared/data/mockData'
import { MOCK_MASTERS, SERVICES } from '../../shared/data/mockData'
import { MOCK_BUSY_BOOKINGS, MOCK_EXISTING, TODAY_STR } from './mock/bookingMockData'
import { getSlotStatusesForService, isMasterBusyAt as checkMasterBusyAt, type AvailabilitySlotStatus } from './utils/availability'
import { generateSlotTimes } from './utils/timeSlots'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

// ─── Shared ────────────────────────────────────────────────────────────────────

export interface SlotStatus {
  time: string
  taken: boolean
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

export type ManagedSlotStatus = AvailabilitySlotStatus

export function isMasterBusyAt(masterId: string, date: string, startTime: string, durationMin: number): boolean {
  return checkMasterBusyAt(MOCK_EXISTING, masterId, date, startTime, durationMin)
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

  return Promise.resolve(getSlotStatusesForService(service, MOCK_BUSY_BOOKINGS))
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
