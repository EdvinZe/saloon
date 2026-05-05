import type { Master, Service } from '../../shared/data/mockData'
import { SERVICES, MOCK_MASTERS } from '../../shared/data/mockData'

export type HomeMetrics = {
  openedAt: string
  googleRating: number
  happyClients: number
  satisfactionPercent: number
}

export async function getHomeMetrics(): Promise<HomeMetrics> {
  // Before change on FastAPI:
  // return _api.get('/api/v1/home/metrics').then(r => r.data)

  return Promise.resolve({
    openedAt: '2017-01-01',
    googleRating: 4.9,
    happyClients: 2400,
    satisfactionPercent: 100,
  })
}

export async function getHomeMasters(): Promise<Master[]> {
  // will be:
  // return _api.get('/api/v1/home/masters').then(r => r.data)

  return Promise.resolve(
    MOCK_MASTERS.filter(master => master.isActive !== false)
  )
}


export async function getHomeServices(): Promise<Service[]> {
  return Promise.resolve(
    SERVICES.filter(service => service.isActive)
  )
}