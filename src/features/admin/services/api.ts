import type {
  AdminService,
  AdminServiceCreateInput,
  AdminServiceUpdateInput,
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

export async function getAdminServices(): Promise<AdminService[]> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin services')
  }

  return response.json() as Promise<AdminService[]>
}

export async function getAdminService(id: number): Promise<AdminService> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services/${id}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin service')
  }

  return response.json() as Promise<AdminService>
}

export async function createAdminService(
  payload: AdminServiceCreateInput,
): Promise<AdminService> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to create service')
  }

  return response.json() as Promise<AdminService>
}

export async function updateAdminService(
  id: number,
  payload: AdminServiceUpdateInput,
): Promise<AdminService> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update service')
  }

  return response.json() as Promise<AdminService>
}

export async function activateAdminService(id: number): Promise<AdminService> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services/${id}/activate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to activate service')
  }

  return response.json() as Promise<AdminService>
}

export async function deactivateAdminService(id: number): Promise<AdminService> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/services/${id}/deactivate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to deactivate service')
  }

  return response.json() as Promise<AdminService>
}
