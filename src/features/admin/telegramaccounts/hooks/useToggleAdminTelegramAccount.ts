import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activateAdminTelegramAccount, deactivateAdminTelegramAccount } from '../api'
import { adminTelegramAccountsQueryKey } from './useAdminTelegramAccounts'

type ToggleAdminTelegramAccountVariables = {
  id: number
  nextIsActive: boolean
}

export function useToggleAdminTelegramAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, nextIsActive }: ToggleAdminTelegramAccountVariables) => (
      nextIsActive ? activateAdminTelegramAccount(id) : deactivateAdminTelegramAccount(id)
    ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminTelegramAccountsQueryKey })
    },
  })
}
