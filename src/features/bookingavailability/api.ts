import type { Master } from '../../shared/data/mockData'
import { MOCK_MASTERS, SERVICES } from '../../shared/data/mockData'
import { MOCK_BUSY_BOOKINGS, MOCK_EXISTING } from '../booking/mock/bookingMockData'
import { getSlotStatusesForService, isMasterBusyAt } from '../booking/utils/availability'

export interface AvailableMastersForSlotParams {
  date: string
  time: string
  serviceId?: string
  durationMin?: number
}

export type AvailableSlotStatus = {
  time: string
  status: 'taken' | 'tooShort' | 'free'
}

export interface AvailableSlotsParams {
  date: string
  serviceId: string
  excludeBookingToken?: string
}

export async function getAvailableMastersForSlot(
  params: AvailableMastersForSlotParams
): Promise<Master[]> {
  // Later FastAPI should handle active master, service capability, working schedule,
  // vacations/time off, existing bookings, and excluding current booking during reschedule if needed.
  let masters = MOCK_MASTERS.filter(master => master.isActive)

  if (params.durationMin) {
    masters = masters.filter(master =>
      !isMasterBusyAt(MOCK_EXISTING, master.id, params.date, params.time, params.durationMin!)
    )
  }

  return Promise.resolve(masters)
}

export async function getAvailableSlotsForService(
  params: AvailableSlotsParams
): Promise<AvailableSlotStatus[]> {
  // Later FastAPI should calculate this using service duration, buffer, master schedules,
  // vacations/time off, existing bookings, business hours, and excludeBookingToken for reschedule flow.
  void params.date
  void params.excludeBookingToken

  const service = SERVICES.find(s => s.id === params.serviceId)
  if (!service) return Promise.resolve([])

  return Promise.resolve(getSlotStatusesForService(service, MOCK_BUSY_BOOKINGS))
}
