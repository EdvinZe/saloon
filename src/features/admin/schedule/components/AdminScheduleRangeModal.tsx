import { useState } from 'react'
import type { AdminEditableScheduleStatus, AdminScheduleMaster } from '../types'

const editableStatuses: AdminEditableScheduleStatus[] = [
  'working',
  'extra_day',
  'day_off',
  'vacation',
  'sick',
  'other',
]

type AdminScheduleRangeModalProps = {
  masters: AdminScheduleMaster[]
  fromDate: string
  toDate: string
  isSaving: boolean
  errorMessage?: string | null
  onClose: () => void
  onSave: (payload: {
    master_id: number
    from_date: string
    to_date: string
    status: AdminEditableScheduleStatus
    start_time: string | null
    end_time: string | null
    note: string | null
  }) => void
}

export default function AdminScheduleRangeModal({
  masters,
  fromDate,
  toDate,
  isSaving,
  errorMessage,
  onClose,
  onSave,
}: AdminScheduleRangeModalProps) {
  const [masterId, setMasterId] = useState(masters[0]?.id ?? 0)
  const [draftFromDate, setDraftFromDate] = useState(fromDate)
  const [draftToDate, setDraftToDate] = useState(toDate)
  const [status, setStatus] = useState<AdminEditableScheduleStatus>('working')
  const [startTime, setStartTime] = useState('10:00')
  const [endTime, setEndTime] = useState('20:00')
  const [note, setNote] = useState('')
  const usesTime = status === 'working' || status === 'extra_day'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <form
        className="w-full max-w-xl border border-[#2a2218] bg-[#141008] p-5 shadow-2xl"
        onSubmit={event => {
          event.preventDefault()
          onSave({
            master_id: masterId,
            from_date: draftFromDate,
            to_date: draftToDate,
            status,
            start_time: usesTime ? startTime : null,
            end_time: usesTime ? endTime : null,
            note: note.trim() || null,
          })
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#c9a84c]">Update range</p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">Apply schedule to dates</h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm text-[#7a7060]">
            Master
            <select
              value={masterId}
              onChange={event => setMasterId(Number(event.target.value))}
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
              required
            >
              {masters.map(master => (
                <option key={master.id} value={master.id}>{master.name}</option>
              ))}
            </select>
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              From date
              <input
                type="date"
                value={draftFromDate}
                onChange={event => setDraftFromDate(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-[#7a7060]">
              To date
              <input
                type="date"
                value={draftToDate}
                onChange={event => setDraftToDate(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
          </div>

          <label className="grid gap-2 text-sm text-[#7a7060]">
            Status
            <select
              value={status}
              onChange={event => setStatus(event.target.value as AdminEditableScheduleStatus)}
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
            >
              {editableStatuses.map(value => (
                <option key={value} value={value}>{value.replace('_', ' ')}</option>
              ))}
            </select>
          </label>

          {usesTime ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm text-[#7a7060]">
                Start time
                <input
                  type="time"
                  value={startTime}
                  onChange={event => setStartTime(event.target.value)}
                  className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                  required
                />
              </label>
              <label className="grid gap-2 text-sm text-[#7a7060]">
                End time
                <input
                  type="time"
                  value={endTime}
                  onChange={event => setEndTime(event.target.value)}
                  className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                  required
                />
              </label>
            </div>
          ) : null}

          <label className="grid gap-2 text-sm text-[#7a7060]">
            Note
            <textarea
              value={note}
              onChange={event => setNote(event.target.value)}
              placeholder="Optional note"
              className="min-h-24 border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
            />
          </label>
        </div>

        {errorMessage ? <p className="mt-4 text-sm text-rose-300">{errorMessage}</p> : null}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="px-4 py-2 text-sm text-[#7a7060]" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn-gold px-5 py-2 text-xs" disabled={isSaving || masterId === 0}>
            {isSaving ? 'Saving...' : 'Save range'}
          </button>
        </div>
      </form>
    </div>
  )
}
