import axios from 'axios'
import type { Master } from '../../shared/data/mockData'
import { MOCK_MASTERS } from '../../shared/data/mockData'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

export interface SlotStatus {
  time: string
  taken: boolean
}

const TAKEN_TIMES = new Set(['09:00', '10:30', '13:00', '15:30', '17:00'])

export async function getAvailableSlots(_date: string): Promise<SlotStatus[]> {
  // Replace with: return _api.get(`/slots?date=${_date}`).then(r => r.data)
  const slots: SlotStatus[] = []
  for (let h = 9; h <= 18; h++) {
    for (const m of [0, 30]) {
      if (h === 18 && m === 30) break
      const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      slots.push({ time, taken: TAKEN_TIMES.has(time) })
    }
  }
  return Promise.resolve(slots)
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
