import type {
  AdminMaster,
  AdminMasterCreateInput,
  AdminMasterUpdateInput,
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

export async function getAdminMasters(): Promise<AdminMaster[]> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin masters')
  }

  return response.json() as Promise<AdminMaster[]>
}

export async function getAdminMaster(id: number): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters/${id}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin master')
  }

  return response.json() as Promise<AdminMaster>
}

export async function createAdminMaster(
  payload: AdminMasterCreateInput,
): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to create master')
  }

  return response.json() as Promise<AdminMaster>
}

export async function updateAdminMaster(
  id: number,
  payload: AdminMasterUpdateInput,
): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update master')
  }

  return response.json() as Promise<AdminMaster>
}

export async function activateAdminMaster(id: number): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters/${id}/activate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to activate master')
  }

  return response.json() as Promise<AdminMaster>
}

export async function deactivateAdminMaster(id: number): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters/${id}/deactivate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to deactivate master')
  }

  return response.json() as Promise<AdminMaster>
}

export async function updateAdminMasterServices(
  id: number,
  serviceIds: number[],
): Promise<AdminMaster> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/masters/${id}/services`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ service_ids: serviceIds }),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update master services')
  }

  return response.json() as Promise<AdminMaster>
}
