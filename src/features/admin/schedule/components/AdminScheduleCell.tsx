import type { AdminScheduleDay, AdminScheduleMaster, AdminScheduleStatus } from '../types'

const statusLabels: Record<AdminScheduleStatus, string> = {
  working: 'Working',
  extra_day: 'Extra day',
  day_off: 'Day off',
  vacation: 'Vacation',
  sick: 'Sick',
  other: 'Other',
  not_set: 'Off',
}

const statusClasses: Record<AdminScheduleStatus, string> = {
  working: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100',
  extra_day: 'border-[#c9a84c]/40 bg-[#c9a84c]/10 text-[#f2d985]',
  day_off: 'border-zinc-700 bg-zinc-900/70 text-zinc-300',
  vacation: 'border-sky-500/30 bg-sky-500/10 text-sky-100',
  sick: 'border-rose-500/30 bg-rose-500/10 text-rose-100',
  other: 'border-amber-500/30 bg-amber-500/10 text-amber-100',
  not_set: 'border-zinc-800 bg-[#111] text-zinc-500',
}

type AdminScheduleCellProps = {
  master: AdminScheduleMaster
  day: AdminScheduleDay
  onClick: (master: AdminScheduleMaster, day: AdminScheduleDay) => void
}

export default function AdminScheduleCell({ master, day, onClick }: AdminScheduleCellProps) {
  const isTimed = day.status === 'working' || day.status === 'extra_day'
  const timeRange = isTimed && day.start_time && day.end_time
    ? `${day.start_time}-${day.end_time}`
    : null

  return (
    <button
      type="button"
      onClick={() => onClick(master, day)}
      className={`min-h-[92px] w-full rounded-md border p-3 text-left transition hover:border-[#c9a84c]/70 hover:bg-[#1a150d] ${statusClasses[day.status]}`}
    >
      <span className="block text-[11px] uppercase tracking-[0.18em]">
        {statusLabels[day.status]}
      </span>
      <span className="mt-2 block text-sm font-semibold text-inherit">
        {timeRange ?? (day.status === 'not_set' ? '+ Add' : statusLabels[day.status])}
      </span>
      {day.note ? (
        <span className="mt-2 block truncate text-xs opacity-75">{day.note}</span>
      ) : null}
    </button>
  )
}
