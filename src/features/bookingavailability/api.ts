import type { Master, MasterService } from '../masters/api'

type ApiMaster = {
  id: number
  name: string
  role: string
  bio: string
  initials: string
  services: MasterService[]
}

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

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
}

function mapMaster(apiMaster: ApiMaster): Master {
  return {
    id: apiMaster.id,
    name: apiMaster.name,
    role: apiMaster.role,
    bio: apiMaster.bio,
    initials: apiMaster.initials,
    services: apiMaster.services,
  }
}

export async function getAvailableMastersForSlot(
  params: AvailableMastersForSlotParams
): Promise<Master[]> {
  if (typeof params.serviceId !== 'number' || !Number.isFinite(params.serviceId)) {
    return []
  }

  const searchParams = new URLSearchParams({
    service_id: String(params.serviceId),
    date: params.date,
    time: params.time,
  })
  const response = await fetch(`${API_BASE_URL}/api/availability/masters?${searchParams}`)

  if (!response.ok) {
    throw new Error('Failed to fetch available masters')
  }

  const data = await response.json() as ApiMaster[]
  return data.map(mapMaster)
}

export async function getAvailableSlotsForService(
  params: AvailableSlotsParams
): Promise<AvailableSlotStatus[]> {
  const searchParams = new URLSearchParams({
    service_id: String(params.serviceId),
    date: params.date,
  })
  const response = await fetch(`${API_BASE_URL}/api/availability/slots?${searchParams}`)

  if (!response.ok) {
    throw new Error('Failed to fetch available slots')
  }

  return response.json() as Promise<AvailableSlotStatus[]>
}
