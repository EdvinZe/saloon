import { useQuery } from '@tanstack/react-query'
import { getAdminTelegramAccounts } from '../api'

export const adminTelegramAccountsQueryKey = ['admin-telegram-accounts']

export function useAdminTelegramAccounts() {
  return useQuery({
    queryKey: adminTelegramAccountsQueryKey,
    queryFn: getAdminTelegramAccounts,
    staleTime: 60_000,
  })
}
