import {
  adminToolbarActionsEndClassName,
  adminToolbarClassName,
} from '../../layout/adminStyles'

type AdminScheduleToolbarProps = {
  fromDate: string
  toDate: string
  draftFromDate: string
  draftToDate: string
  onDraftFromDateChange: (value: string) => void
  onDraftToDateChange: (value: string) => void
  onApplyRange: () => void
  onPreviousWeek: () => void
  onThisWeek: () => void
  onNextWeek: () => void
  onOpenRangeModal: () => void
}

export default function AdminScheduleToolbar({
  fromDate,
  toDate,
  draftFromDate,
  draftToDate,
  onDraftFromDateChange,
  onDraftToDateChange,
  onApplyRange,
  onPreviousWeek,
  onThisWeek,
  onNextWeek,
  onOpenRangeModal,
}: AdminScheduleToolbarProps) {
  return (
    <div className={adminToolbarClassName}>
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Schedule</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Master shifts</h1>
        <p className="mt-1 text-sm text-[#7a7060]">{fromDate} to {toDate}</p>
      </div>

      <div className={adminToolbarActionsEndClassName}>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onPreviousWeek}>
          Previous week
        </button>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onThisWeek}>
          This week
        </button>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onNextWeek}>
          Next week
        </button>
        <label className="flex flex-col gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          From
          <input
            type="date"
            value={draftFromDate}
            onChange={event => onDraftFromDateChange(event.target.value)}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          To
          <input
            type="date"
            value={draftToDate}
            onChange={event => onDraftToDateChange(event.target.value)}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          />
        </label>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onApplyRange}>
          Set range
        </button>
        <button
          type="button"
          className="border border-[#c9a84c] bg-[#c9a84c] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#0f0f0f]"
          onClick={onOpenRangeModal}
        >
          Update range
        </button>
      </div>
    </div>
  )
}
