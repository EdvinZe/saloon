import axios from 'axios'
import { addDays, format } from 'date-fns'
import type { Service } from '../services/api'
import { getServices } from '../services/api'
import { getAvailableMastersForSlot, getAvailableSlotsForService, type AvailableSlotStatus } from '../bookingavailability/api'
import { MOCK_EXISTING, TODAY_STR } from './mock/bookingMockData'
import { isMasterBusyAt as checkMasterBusyAt } from './utils/availability'
import { getMasters, type Master } from '../masters/api'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'
const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

async function buildApiError(response: Response, fallbackMessage: string) {
  const responseText = await response.text()
  let responseBody: unknown = responseText

  try {
    responseBody = responseText ? JSON.parse(responseText) : null
  } catch {
    responseBody = responseText
  }

  return Object.assign(new Error(fallbackMessage), {
    status: response.status,
    url: response.url,
    responseBody,
  })
}

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

export async function getAvailableSlots(_date: string, serviceId?: number): Promise<SlotStatus[]> {
  if (typeof serviceId !== 'number' || !Number.isFinite(serviceId)) {
    return []
  }

  const slots = await getAvailableSlotsForService({ date: _date, serviceId })
  return slots.map(slot => ({
    time: slot.time,
    taken: slot.status !== 'free',
  }))
}

export async function getAvailableMasters(date: string, time: string, serviceId: number): Promise<Master[]> {
  return getAvailableMastersForSlot({ date, time, serviceId })
}

export async function getNearestAvailableSlot(serviceId: number): Promise<NearestAvailableSlot | null> {
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
  service_id: number
  master_id: number
  date: string
  time: string
  customer_first_name: string
  customer_last_name: string
  customer_phone: string
  customer_email: string
}

export interface BookingCheckPayload {
  service_id: number
  master_id: number
  date: string
  time: string
  customer_first_name: string
  customer_last_name: string
  customer_phone: string
  customer_email: string
}

export interface BookingAvailabilityCheckResponse {
  available: boolean
  message: string
}

export interface BookingDepositIntentResponse {
  client_secret: string
  payment_intent_id: string
}

export async function createBooking(data: BookingPayload) {
  return _api.post('/bookings', data).then(r => r.data)
}

export async function checkBookingAvailability(
  payload: BookingCheckPayload
): Promise<BookingAvailabilityCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/api/bookings/check-availability`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to check booking availability')
  }

  return response.json() as Promise<BookingAvailabilityCheckResponse>
}

export async function createBookingDepositIntent(
  payload: BookingCheckPayload
): Promise<BookingDepositIntentResponse> {
  const response = await fetch(`${API_BASE_URL}/api/bookings/deposit-intent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to create booking deposit intent')
  }

  return response.json() as Promise<BookingDepositIntentResponse>
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

export function isMasterBusyAt(masterId: number, date: string, startTime: string, durationMin: number): boolean {
  return checkMasterBusyAt(MOCK_EXISTING, masterId, date, startTime, durationMin)
}

export async function getBookingByToken(_token: string): Promise<ManagedBooking> {
  // Replace with: return _api.get(`/api/v1/bookings/manage?token=${_token}`).then(r => r.data)
  const services = await getServices()
  const masters = await getMasters()
  const master = masters[0]

  if (!master) {
    throw new Error('Failed to fetch masters')
  }

  return Promise.resolve({
    id: 'BK-001',
    service: services[0],
    date: TODAY_STR,
    time: '09:30',
    master,
    depositPaid: 10,
    status: 'confirmed' as const,
  })
}

export async function getSlotsForService(date: string, serviceId: number): Promise<ManagedSlotStatus[]> {
  // Replace with: return _api.get(`/api/v1/bookings/slots?date=${date}&service_id=${serviceId}`).then(r => r.data)
  return getAvailableSlotsForService({ date, serviceId })
}

export interface ReschedulePayload {
  token: string
  serviceId: number
  date: string
  time: string
  masterId: number
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
