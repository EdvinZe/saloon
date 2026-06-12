import type {
  AdminScheduleDay,
  AdminScheduleDayUpsert,
  AdminScheduleRangeResponse,
  AdminScheduleRangeUpsert,
  AdminScheduleResponse,
} from './types'
import { adminFetch } from '../auth/api'

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

export async function getAdminSchedule(params: {
  fromDate: string
  toDate: string
}): Promise<AdminScheduleResponse> {
  const searchParams = new URLSearchParams({
    from_date: params.fromDate,
    to_date: params.toDate,
  })
  const response = await adminFetch(`${API_BASE_URL}/api/admin/schedule/?${searchParams.toString()}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin schedule')
  }

  return response.json() as Promise<AdminScheduleResponse>
}

export async function updateAdminScheduleDay(
  payload: AdminScheduleDayUpsert,
): Promise<AdminScheduleDay> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/schedule/day`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update schedule day')
  }

  return response.json() as Promise<AdminScheduleDay>
}

export async function updateAdminScheduleRange(
  payload: AdminScheduleRangeUpsert,
): Promise<AdminScheduleRangeResponse> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/schedule/range`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update schedule range')
  }

  return response.json() as Promise<AdminScheduleRangeResponse>
}
