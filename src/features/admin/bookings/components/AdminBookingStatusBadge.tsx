import type { AdminBookingStatus } from '../types'

type AdminBookingStatusBadgeProps = {
  status: AdminBookingStatus | string
}

const statusClasses: Record<string, string> = {
  confirmed: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100',
  cancelled: 'border-zinc-700 bg-zinc-900/70 text-zinc-400',
  completed: 'border-[#c9a84c]/40 bg-[#c9a84c]/10 text-[#f2d985]',
  no_show: 'border-rose-500/30 bg-rose-500/10 text-rose-100',
}

export default function AdminBookingStatusBadge({ status }: AdminBookingStatusBadgeProps) {
  return (
    <span className={`border px-2 py-1 text-[11px] uppercase tracking-[0.16em] ${statusClasses[status] ?? statusClasses.cancelled}`}>
      {status.replace('_', ' ')}
    </span>
  )
}
