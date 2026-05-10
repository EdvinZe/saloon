import axios from 'axios'
import { addDays, format } from 'date-fns'
import type { Master, Service } from '../../shared/data/mockData'
import { MOCK_MASTERS, SERVICES } from '../../shared/data/mockData'
import { getAvailableMastersForSlot, getAvailableSlotsForService, type AvailableSlotStatus } from '../bookingavailability/api'
import { MOCK_EXISTING, TODAY_STR } from './mock/bookingMockData'
import { isMasterBusyAt as checkMasterBusyAt } from './utils/availability'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

// ─── Shared ────────────────────────────────────────────────────────────────────

export interface SlotStatus {
  time: string
  taken: boolean
}

export interface NearestAvailableSlot {
  date: string
  time: string
}

// ─── New-booking API ────────────────────────────────────────────────────────────

export async function getAvailableSlots(_date: string): Promise<SlotStatus[]> {
  const slots = await getAvailableSlotsForService({ date: _date, serviceId: 'haircut' })
  return slots.map(slot => ({
    time: slot.time,
    taken: slot.status !== 'free',
  }))
}

export async function getAvailableMasters(date: string, time: string, serviceId: string): Promise<Master[]> {
  return getAvailableMastersForSlot({ date, time, serviceId })
}

export async function getNearestAvailableSlot(serviceId: string): Promise<NearestAvailableSlot | null> {
  // Replace with FastAPI endpoint: return _api.get(`/api/v1/bookings/nearest-slot?service_id=${serviceId}`).then(r => r.data)
  const today = new Date(TODAY_STR + 'T12:00:00')

  for (let offset = 0; offset < 30; offset += 1) {
    const date = format(addDays(today, offset), 'yyyy-MM-dd')
    const slots = await getSlotsForService(date, serviceId)
    const freeSlot = slots.find(slot => slot.status === 'free')

    if (freeSlot) {
      return { date, time: freeSlot.time }
    }
  }

  return null
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

export type ManagedSlotStatus = AvailableSlotStatus

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
    depositPaid: 10,
    status: 'confirmed' as const,
  })
}

export async function getSlotsForService(date: string, serviceId: string): Promise<ManagedSlotStatus[]> {
  // Replace with: return _api.get(`/api/v1/bookings/slots?date=${date}&service_id=${serviceId}`).then(r => r.data)
  return getAvailableSlotsForService({ date, serviceId })
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
