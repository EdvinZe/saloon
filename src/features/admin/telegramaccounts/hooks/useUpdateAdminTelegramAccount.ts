import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateAdminTelegramAccount } from '../api'
import { adminTelegramAccountsQueryKey } from './useAdminTelegramAccounts'
import type { AdminTelegramAccountUpdateInput } from '../types'

type UpdateAdminTelegramAccountVariables = {
  id: number
  payload: AdminTelegramAccountUpdateInput
}

export function useUpdateAdminTelegramAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: UpdateAdminTelegramAccountVariables) => (
      updateAdminTelegramAccount(id, payload)
    ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminTelegramAccountsQueryKey })
    },
  })
}
