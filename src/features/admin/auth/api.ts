import type { AdminAuthState, AdminLoginPayload } from './types'

const API_BASE_URL = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL

async function buildApiError(response: Response, fallbackMessage: string) {
  const responseText = await response.text()
  let responseBody: unknown

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

export function adminFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  return fetch(input, {
    ...init,
    credentials: 'include',
  }).then(response => {
    if (response.status === 401 && !window.location.pathname.startsWith('/admin/login')) {
      const next = `${window.location.pathname}${window.location.search}`
      window.location.assign(`/admin/login?next=${encodeURIComponent(next)}`)
    }
    return response
  })
}

export async function getAdminMe(): Promise<AdminAuthState> {
  const response = await fetch(`${API_BASE_URL}/api/admin/auth/me`, {
    credentials: 'include',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Admin session is not authenticated')
  }

  return response.json() as Promise<AdminAuthState>
}

export async function loginAdmin(payload: AdminLoginPayload): Promise<AdminAuthState> {
  const response = await fetch(`${API_BASE_URL}/api/admin/auth/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Invalid username or password')
  }

  return response.json() as Promise<AdminAuthState>
}

export async function logoutAdmin(): Promise<AdminAuthState> {
  const response = await fetch(`${API_BASE_URL}/api/admin/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!response.ok) {
    throw await buildApiError(response, 'Could not log out')
  }

  return response.json() as Promise<AdminAuthState>
}
