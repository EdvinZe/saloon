import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { useAdminLogin, useAdminMe } from '../../features/admin/auth/hooks'

function getErrorMessage(error: unknown) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    (error as { status?: unknown }).status === 401
  ) {
    return 'Invalid username or password.'
  }
  return 'Could not sign in. Please try again.'
}

export default function AdminLoginPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const next = params.get('next') || '/admin'
  const meQuery = useAdminMe()
  const loginMutation = useAdminLogin()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    if (meQuery.data?.authenticated) {
      navigate(next, { replace: true })
    }
  }, [meQuery.data?.authenticated, navigate, next])

  if (meQuery.data?.authenticated) {
    return <Navigate replace to={next} />
  }

  const submitLogin = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    loginMutation.mutate(
      { username: username.trim(), password },
      {
        onSuccess: () => navigate(next, { replace: true }),
      },
    )
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] px-5 py-16">
      <div className="mx-auto w-full max-w-md border border-[#2a2218] bg-[#141008] p-6 shadow-2xl">
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Admin access</p>
        <h1 className="mt-3 text-2xl font-normal text-[#e8e0d0]">Sign in to manage bookings</h1>

        <form className="mt-7 grid gap-4" onSubmit={submitLogin}>
          <label className="grid gap-2 text-sm text-[#7a7060]">
            Username
            <input
              value={username}
              onChange={event => setUsername(event.target.value)}
              autoComplete="username"
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-3 text-[#e8e0d0] outline-none focus:border-[#c9a84c]"
              required
            />
          </label>

          <label className="grid gap-2 text-sm text-[#7a7060]">
            Password
            <input
              type="password"
              value={password}
              onChange={event => setPassword(event.target.value)}
              autoComplete="current-password"
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-3 text-[#e8e0d0] outline-none focus:border-[#c9a84c]"
              required
            />
          </label>

          {loginMutation.isError ? (
            <div className="border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">
              {getErrorMessage(loginMutation.error)}
            </div>
          ) : null}

          <button
            type="submit"
            className="btn-gold mt-2 px-5 py-3 text-xs disabled:cursor-not-allowed disabled:opacity-50"
            disabled={loginMutation.isPending || !username.trim() || !password}
          >
            {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
