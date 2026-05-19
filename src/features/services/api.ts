type ApiService = {
  id: number
  name: string
  description: string
  duration_minutes: number
  cleanup_time_minutes: number
  total_duration_minutes: number
  price: string
}

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

export type Service = {
  id: number
  name: string
  description: string
  durationMinutes: number
  cleanupTimeMinutes: number
  totalDurationMinutes: number
  price: string
}

function mapService(apiService: ApiService): Service {
  return {
    id: apiService.id,
    name: apiService.name,
    description: apiService.description,
    durationMinutes: apiService.duration_minutes,
    cleanupTimeMinutes: apiService.cleanup_time_minutes,
    totalDurationMinutes: apiService.total_duration_minutes,
    price: apiService.price,
  }
}

export async function getServices(): Promise<Service[]> {
  const response = await fetch(`${API_BASE_URL}/api/services/public`)

  if (!response.ok) {
    throw new Error('Failed to fetch services')
  }

  const data = await response.json() as ApiService[]

  return data.map(mapService)
}
