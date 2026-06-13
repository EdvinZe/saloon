import { useNavigate } from 'react-router-dom'
import { useAdminLogout } from '../auth/hooks'
import { adminHeaderClassName } from './adminStyles'

export default function AdminHeader() {
  const navigate = useNavigate()
  const logoutMutation = useAdminLogout()

  const logout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => navigate('/admin/login', { replace: true }),
    })
  }

  return (
    <header className={adminHeaderClassName}>
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#7a7060]">Admin panel</p>
        <h2 className="mt-1 text-lg text-[#e8e0d0]">Barbershop management</h2>
      </div>
      <div className="flex self-end justify-end pr-8 sm:self-auto">
        <button
          type="button"
          className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c] disabled:cursor-not-allowed disabled:opacity-50"
          onClick={logout}
          disabled={logoutMutation.isPending}
        >
          {logoutMutation.isPending ? 'Signing out...' : 'Logout'}
        </button>
      </div>
    </header>
  )
}
