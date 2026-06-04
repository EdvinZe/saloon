import { useQuery } from '@tanstack/react-query'
import { getAdminReportSummary } from '../api'

export function useAdminReportSummary(
  fromDate: string,
  toDate: string,
  masterId?: number | null,
) {
  return useQuery({
    queryKey: ['admin-report-summary', fromDate, toDate, masterId ?? null],
    queryFn: () => getAdminReportSummary({ fromDate, toDate, masterId }),
    enabled: Boolean(fromDate && toDate),
    staleTime: 30_000,
  })
}
