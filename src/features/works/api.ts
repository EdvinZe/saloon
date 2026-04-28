import axios from 'axios'
import type { WorkPhoto } from '../../shared/data/mockData'
import { MOCK_WORKS } from '../../shared/data/mockData'

const BASE_URL = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL ?? 'http://localhost:8000'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _api = axios.create({ baseURL: BASE_URL })

export interface WorksPage {
  items: WorkPhoto[]
  has_more: boolean
  total: number
}

export async function getWorks(page: number, limit: number): Promise<WorksPage> {
  // Replace with: return _api.get(`/api/v1/works?page=${page}&limit=${limit}`).then(r => r.data)
  const start = (page - 1) * limit
  const items = MOCK_WORKS.slice(start, start + limit)
  return Promise.resolve({
    items,
    has_more: start + limit < MOCK_WORKS.length,
    total: MOCK_WORKS.length,
  })
}
