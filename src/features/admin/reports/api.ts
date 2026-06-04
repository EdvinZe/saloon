import type { AdminReportSummary, AdminReportSummaryParams } from './types'

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

export async function getAdminReportSummary(
  params: AdminReportSummaryParams,
): Promise<AdminReportSummary> {
  const searchParams = new URLSearchParams({
    from_date: params.fromDate,
    to_date: params.toDate,
  })

  if (params.masterId != null) {
    searchParams.set('master_id', String(params.masterId))
  }

  const response = await fetch(
    `${API_BASE_URL}/api/admin/reports/summary?${searchParams.toString()}`,
  )

  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch admin report summary')
  }

  return response.json() as Promise<AdminReportSummary>
}
