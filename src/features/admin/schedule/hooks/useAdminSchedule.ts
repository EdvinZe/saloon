import { useQuery } from '@tanstack/react-query'
import { getAdminSchedule } from '../api'

export const adminScheduleQueryKey = (fromDate: string | null, toDate: string | null) => [
  'admin-schedule',
  fromDate,
  toDate,
]

export function useAdminSchedule(fromDate: string | null, toDate: string | null) {
  return useQuery({
    queryKey: adminScheduleQueryKey(fromDate, toDate),
    queryFn: () => getAdminSchedule({
      fromDate: fromDate!,
      toDate: toDate!,
    }),
    enabled: Boolean(fromDate && toDate),
    staleTime: 30_000,
  })
}
