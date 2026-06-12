import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAdminMe } from '../hooks'

type ProtectedAdminRouteProps = {
  children: ReactNode
}

export default function ProtectedAdminRoute({ children }: ProtectedAdminRouteProps) {
  const location = useLocation()
  const { data, isLoading, isError } = useAdminMe()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
        Checking admin session...
      </div>
    )
  }

  if (isError || data?.authenticated !== true) {
    const next = `${location.pathname}${location.search}`
    return <Navigate replace to={`/admin/login?next=${encodeURIComponent(next)}`} />
  }

  return <>{children}</>
}
