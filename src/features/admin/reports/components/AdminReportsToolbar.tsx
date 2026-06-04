import type { AdminMaster } from '../../masters/types'

export type ReportPresetKey =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'last_week'
  | 'this_month'
  | 'last_month'
  | 'this_year'

type AdminReportsToolbarProps = {
  fromDate: string
  toDate: string
  masterId: number | 'all'
  masters: AdminMaster[]
  activePreset: ReportPresetKey | 'custom'
  onPresetSelect: (preset: ReportPresetKey) => void
  onFromDateChange: (value: string) => void
  onToDateChange: (value: string) => void
  onMasterChange: (value: number | 'all') => void
}

const presetButtons: { key: ReportPresetKey; label: string }[] = [
  { key: 'today', label: 'Today' },
  { key: 'yesterday', label: 'Yesterday' },
  { key: 'this_week', label: 'This week' },
  { key: 'last_week', label: 'Last week' },
  { key: 'this_month', label: 'This month' },
  { key: 'last_month', label: 'Last month' },
  { key: 'this_year', label: 'This year' },
]

export default function AdminReportsToolbar({
  fromDate,
  toDate,
  masterId,
  masters,
  activePreset,
  onPresetSelect,
  onFromDateChange,
  onToDateChange,
  onMasterChange,
}: AdminReportsToolbarProps) {
  return (
    <div className="grid gap-4 border border-[#2a2218] bg-[#141008] p-4">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Reports</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Business summary</h1>
      </div>

      <div className="flex flex-wrap gap-2">
        {presetButtons.map(preset => (
          <button
            key={preset.key}
            type="button"
            onClick={() => onPresetSelect(preset.key)}
            className={`border px-3 py-2 text-xs uppercase tracking-[0.12em] ${
              activePreset === preset.key
                ? 'border-[#c9a84c] bg-[#c9a84c]/10 text-[#e8e0d0]'
                : 'border-[#2a2218] bg-[#0f0f0f] text-[#7a7060] hover:text-[#e8e0d0]'
            }`}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          From date
          <input
            type="date"
            value={fromDate}
            onChange={event => onFromDateChange(event.target.value)}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          />
        </label>
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          To date
          <input
            type="date"
            value={toDate}
            onChange={event => onToDateChange(event.target.value)}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          />
        </label>
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          Master
          <select
            value={masterId}
            onChange={event => onMasterChange(event.target.value === 'all' ? 'all' : Number(event.target.value))}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          >
            <option value="all">All masters</option>
            {masters.map(master => (
              <option key={master.id} value={master.id}>{master.name}</option>
            ))}
          </select>
        </label>
      </div>
    </div>
  )
}
