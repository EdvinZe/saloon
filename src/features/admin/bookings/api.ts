import type {
  AdminBooking,
  AdminBookingActionResponse,
  AdminBookingListParams,
} from './types'

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

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

export async function getAdminBookings(
  params: AdminBookingListParams,
): Promise<AdminBooking[]> {
  const searchParams = new URLSearchParams()

  if (params.date) searchParams.set('date', params.date)
  if (params.status) searchParams.set('status', params.status)
  if (params.masterId) searchParams.set('master_id', String(params.masterId))
  if (params.serviceId) searchParams.set('service_id', String(params.serviceId))

  const query = searchParams.toString()
  const response = await fetch(`${API_BASE_URL}/api/admin/bookings${query ? `?${query}` : ''}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin bookings')
  }

  return response.json() as Promise<AdminBooking[]>
}

export async function getAdminBooking(id: number): Promise<AdminBooking> {
  const response = await fetch(`${API_BASE_URL}/api/admin/bookings/${id}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin booking')
  }

  return response.json() as Promise<AdminBooking>
}

export async function completeAdminBooking(id: number): Promise<AdminBookingActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/bookings/${id}/complete`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to complete booking')
  }

  return response.json() as Promise<AdminBookingActionResponse>
}

export async function noShowAdminBooking(id: number): Promise<AdminBookingActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/bookings/${id}/no-show`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to mark booking no-show')
  }

  return response.json() as Promise<AdminBookingActionResponse>
}

export async function cancelAdminBooking(id: number): Promise<AdminBookingActionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/admin/bookings/${id}/cancel`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to cancel booking')
  }

  return response.json() as Promise<AdminBookingActionResponse>
}
