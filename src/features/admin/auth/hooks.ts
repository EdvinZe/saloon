import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getAdminMe, loginAdmin, logoutAdmin } from './api'

export const adminMeQueryKey = ['admin-auth', 'me'] as const

export function useAdminMe(enabled = true) {
  return useQuery({
    queryKey: adminMeQueryKey,
    queryFn: getAdminMe,
    enabled,
    retry: false,
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  })
}

export function useAdminLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: loginAdmin,
    onSuccess: data => {
      queryClient.setQueryData(adminMeQueryKey, data)
    },
  })
}

export function useAdminLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: logoutAdmin,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: adminMeQueryKey })
    },
  })
}
