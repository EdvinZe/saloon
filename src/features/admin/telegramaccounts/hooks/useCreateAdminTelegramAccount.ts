import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createAdminTelegramAccount } from '../api'
import { adminTelegramAccountsQueryKey } from './useAdminTelegramAccounts'

export function useCreateAdminTelegramAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createAdminTelegramAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminTelegramAccountsQueryKey })
    },
  })
}
