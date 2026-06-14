import axios from 'axios'
import { addDays, format } from 'date-fns'
import type { Service } from '../services/api'
import { getServices } from '../services/api'
import { getAvailableMastersForSlot, getAvailableSlotsForService, type AvailableSlotStatus } from '../bookingavailability/api'
import { MOCK_EXISTING, TODAY_STR } from './mock/bookingMockData'
import { isMasterBusyAt as checkMasterBusyAt } from './utils/availability'
import { getMasters, type Master } from '../masters/api'

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: API_BASE_URL })

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

export type BookingPaymentResultStatus =
  | 'confirmed'
  | 'processing'
  | 'failed'
  | 'not_found'
  | 'lookup_failed'
  | 'recovery_failed'

export interface BookingPaymentResult {
  status: BookingPaymentResultStatus
  message: string
  booking: {
    id: number
    booking_code: string | null
    manage_token: string
    manage_url: string
    service_id: number
    master_id: number
    customer_first_name: string
    customer_last_name: string
    customer_phone: string
    customer_email: string
    start_at: string
    end_at: string
    status: string
    deposit_status: string
    source: string
    deposit_amount_cents: number
    currency: string
  } | null
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

export async function getBookingPaymentResult(paymentIntentId: string): Promise<BookingPaymentResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/bookings/payment-result?payment_intent=${encodeURIComponent(paymentIntentId)}`
  )

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to get booking payment result')
  }

  return response.json() as Promise<BookingPaymentResult>
}

// ─── Manage-booking API ─────────────────────────────────────────────────────────

export interface ManagedBooking {
  id: string
  service: Service
  date: string   // 'yyyy-MM-dd'
  time: string   // 'HH:MM'
  start_at: string
  end_at: string
  master: Master
  depositPaid: number
  depositStatus: string
  status: string
}

export interface ManagedBookingCancelResponse {
  success: boolean
  message: string
  booking: ManagedBooking
}

export interface ManagedBookingReschedulePayload {
  token: string
  master_id: number
  date: string
  time: string
}

export interface ManagedBookingRescheduleResponse {
  success: boolean
  message: string
  booking: ManagedBooking
}

export type ManagedSlotStatus = AvailableSlotStatus

interface ApiManagedBooking {
  id: number
  booking_code: string | null
  manage_token: string
  manage_url: string
  service_id: number
  master_id: number
  customer_first_name: string
  customer_last_name: string
  customer_phone: string
  customer_email: string
  start_at: string
  end_at: string
  status: string
  deposit_status: string
  source: string
  deposit_amount_cents: number
  currency: string
}

interface ApiManagedBookingCancelResponse {
  success: boolean
  message: string
  booking: ApiManagedBooking
}

interface ApiManagedBookingRescheduleResponse {
  success: boolean
  message: string
  booking: ApiManagedBooking
}

export function isMasterBusyAt(masterId: number, date: string, startTime: string, durationMin: number): boolean {
  return checkMasterBusyAt(MOCK_EXISTING, masterId, date, startTime, durationMin)
}

export async function getBookingByToken(token: string): Promise<ManagedBooking> {
  if (!token.trim()) {
    throw Object.assign(new Error('Booking token is required'), { status: 400 })
  }

  const response = await fetch(
    `${API_BASE_URL}/api/bookings/manage?token=${encodeURIComponent(token.trim())}`
  )

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch managed booking')
  }

  const booking = await response.json() as ApiManagedBooking
  return mapManagedBooking(booking)
}

export async function cancelManagedBooking(token: string): Promise<ManagedBookingCancelResponse> {
  if (!token.trim()) {
    throw Object.assign(new Error('Booking token is required'), { status: 400 })
  }

  const response = await fetch(`${API_BASE_URL}/api/bookings/manage/cancel`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token: token.trim() }),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to cancel booking')
  }

  const data = await response.json() as ApiManagedBookingCancelResponse
  return {
    success: data.success,
    message: data.message,
    booking: await mapManagedBooking(data.booking),
  }
}

export async function rescheduleManagedBooking(
  payload: ManagedBookingReschedulePayload
): Promise<ManagedBookingRescheduleResponse> {
  if (!payload.token.trim()) {
    throw Object.assign(new Error('Booking token is required'), { status: 400 })
  }

  const response = await fetch(`${API_BASE_URL}/api/bookings/manage/reschedule`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: payload.token.trim(),
      master_id: payload.master_id,
      date: payload.date,
      time: payload.time,
    }),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to reschedule booking')
  }

  const data = await response.json() as ApiManagedBookingRescheduleResponse
  return {
    success: data.success,
    message: data.message,
    booking: await mapManagedBooking(data.booking),
  }
}

async function mapManagedBooking(booking: ApiManagedBooking): Promise<ManagedBooking> {
  const [services, masters] = await Promise.all([
    getServices(),
    getMasters(),
  ])
  const service = services.find(item => item.id === booking.service_id)
  const master = masters.find(item => item.id === booking.master_id)

  if (!service || !master) {
    throw new Error('Failed to load booking details')
  }

  return {
    id: String(booking.id),
    service,
    date: booking.start_at.slice(0, 10),
    time: booking.start_at.slice(11, 16),
    start_at: booking.start_at,
    end_at: booking.end_at,
    master,
    depositPaid: booking.deposit_amount_cents / 100,
    depositStatus: booking.deposit_status,
    status: booking.status,
  }
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
