import type {
  AdminTelegramAccount,
  AdminTelegramAccountCreateInput,
  AdminTelegramAccountUpdateInput,
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

export async function getAdminTelegramAccounts(): Promise<AdminTelegramAccount[]> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch Telegram accounts')
  }

  return response.json() as Promise<AdminTelegramAccount[]>
}

export async function getAdminTelegramAccount(id: number): Promise<AdminTelegramAccount> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts/${id}`)

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch Telegram account')
  }

  return response.json() as Promise<AdminTelegramAccount>
}

export async function createAdminTelegramAccount(
  payload: AdminTelegramAccountCreateInput,
): Promise<AdminTelegramAccount> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to create Telegram account')
  }

  return response.json() as Promise<AdminTelegramAccount>
}

export async function updateAdminTelegramAccount(
  id: number,
  payload: AdminTelegramAccountUpdateInput,
): Promise<AdminTelegramAccount> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to update Telegram account')
  }

  return response.json() as Promise<AdminTelegramAccount>
}

export async function activateAdminTelegramAccount(id: number): Promise<AdminTelegramAccount> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts/${id}/activate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to activate Telegram account')
  }

  return response.json() as Promise<AdminTelegramAccount>
}

export async function deactivateAdminTelegramAccount(id: number): Promise<AdminTelegramAccount> {
  const response = await adminFetch(`${API_BASE_URL}/api/admin/telegram-accounts/${id}/deactivate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to deactivate Telegram account')
  }

  return response.json() as Promise<AdminTelegramAccount>
}
