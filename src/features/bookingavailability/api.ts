import { MOCK_BUSY_BOOKINGS, MOCK_EXISTING } from '../booking/mock/bookingMockData'
import { getSlotStatusesForService, isMasterBusyAt } from '../booking/utils/availability'
import { getMasters, type Master } from '../masters/api'
import { getServices } from '../services/api'

export interface AvailableMastersForSlotParams {
  date: string
  time: string
  serviceId?: number
  durationMin?: number
}

export type AvailableSlotStatus = {
  time: string
  status: 'taken' | 'tooShort' | 'free'
}

export interface AvailableSlotsParams {
  date: string
  serviceId: number
  excludeBookingToken?: string
}

export async function getAvailableMastersForSlot(
  params: AvailableMastersForSlotParams
): Promise<Master[]> {
  // Later FastAPI should handle active master, service capability, working schedule,
  // vacations/time off, existing bookings, and excluding current booking during reschedule if needed.
  const masters = await getMasters(params.serviceId)

  if (params.durationMin) {
    return masters.filter(master =>
      !isMasterBusyAt(MOCK_EXISTING, master.id, params.date, params.time, params.durationMin!)
    )
  }

  return masters
}

export async function getAvailableSlotsForService(
  params: AvailableSlotsParams
): Promise<AvailableSlotStatus[]> {
  // Later FastAPI should calculate this using service duration, buffer, master schedules,
  // vacations/time off, existing bookings, business hours, and excludeBookingToken for reschedule flow.
  void params.date
  void params.excludeBookingToken

  const services = await getServices()
  const service = services.find(s => s.id === params.serviceId)
  if (!service) return Promise.resolve([])

  return Promise.resolve(getSlotStatusesForService(service, MOCK_BUSY_BOOKINGS))
}
