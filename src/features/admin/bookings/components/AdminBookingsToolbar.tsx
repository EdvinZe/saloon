import type { AdminBookingStatus } from '../types'
import type { AdminMaster } from '../../masters/types'
import type { AdminService } from '../../services/types'

type AdminBookingsToolbarProps = {
  date: string
  status: AdminBookingStatus | 'all'
  masterId: number | 'all'
  serviceId: number | 'all'
  masters: AdminMaster[]
  services: AdminService[]
  onDateChange: (value: string) => void
  onStatusChange: (value: AdminBookingStatus | 'all') => void
  onMasterChange: (value: number | 'all') => void
  onServiceChange: (value: number | 'all') => void
  onClearFilters: () => void
}

const statuses: (AdminBookingStatus | 'all')[] = [
  'all',
  'confirmed',
  'cancelled',
  'completed',
  'no_show',
]

export default function AdminBookingsToolbar({
  date,
  status,
  masterId,
  serviceId,
  masters,
  services,
  onDateChange,
  onStatusChange,
  onMasterChange,
  onServiceChange,
  onClearFilters,
}: AdminBookingsToolbarProps) {
  return (
    <div className="flex flex-col gap-4 border border-[#2a2218] bg-[#141008] p-4">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Bookings</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Manage appointments and booking statuses</h1>
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          Date
          <input
            type="date"
            value={date}
            onChange={event => onDateChange(event.target.value)}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          />
        </label>
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          Status
          <select
            value={status}
            onChange={event => onStatusChange(event.target.value as AdminBookingStatus | 'all')}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          >
            {statuses.map(item => (
              <option key={item} value={item}>{item.replace('_', ' ')}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          Master
          <select
            value={masterId}
            onChange={event => onMasterChange(event.target.value === 'all' ? 'all' : Number(event.target.value))}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          >
            <option value="all">all</option>
            {masters.map(master => (
              <option key={master.id} value={master.id}>{master.name}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-xs uppercase tracking-[0.16em] text-[#7a7060]">
          Service
          <select
            value={serviceId}
            onChange={event => onServiceChange(event.target.value === 'all' ? 'all' : Number(event.target.value))}
            className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-sm normal-case tracking-normal text-[#e8e0d0]"
          >
            <option value="all">all</option>
            {services.map(service => (
              <option key={service.id} value={service.id}>{service.name}</option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button type="button" className="btn-gold w-full px-4 py-2 text-xs" onClick={onClearFilters}>
            Clear
          </button>
        </div>
      </div>
    </div>
  )
}
