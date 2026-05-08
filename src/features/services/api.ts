import type { Service } from '../../shared/data/mockData'
import { SERVICES } from '../../shared/data/mockData'

export async function getServices(): Promise<Service[]> {
  return Promise.resolve(
    SERVICES.filter(service => service.isActive)
  )
}