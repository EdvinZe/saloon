import { format } from 'date-fns'
import type { AdminScheduleDay, AdminScheduleMaster, AdminScheduleResponse } from '../types'
import AdminScheduleCell from './AdminScheduleCell'

type AdminScheduleTableProps = {
  schedule: AdminScheduleResponse
  onCellClick: (master: AdminScheduleMaster, day: AdminScheduleDay) => void
}

export default function AdminScheduleTable({ schedule, onCellClick }: AdminScheduleTableProps) {
  return (
    <div className="overflow-x-auto border border-[#2a2218] bg-[#0c0c0b]">
      <table className="min-w-[980px] w-full border-collapse">
        <thead>
          <tr className="border-b border-[#2a2218] bg-[#141008]">
            <th className="sticky left-0 z-10 w-52 bg-[#141008] px-4 py-3 text-left text-xs uppercase tracking-[0.2em] text-[#c9a84c]">
              Master
            </th>
            {schedule.days.map(day => (
              <th key={day} className="min-w-32 px-3 py-3 text-left">
                <span className="block text-sm text-[#e8e0d0]">
                  {format(new Date(`${day}T12:00:00`), 'EEE')}
                </span>
                <span className="block text-xs text-[#7a7060]">
                  {format(new Date(`${day}T12:00:00`), 'MMM d')}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {schedule.masters.map(master => (
            <tr key={master.id} className="border-b border-[#211a12] last:border-b-0">
              <th className="sticky left-0 z-10 w-52 bg-[#0c0c0b] px-4 py-3 text-left align-top">
                <span className="block text-sm text-[#e8e0d0]">{master.name}</span>
                <span className="mt-1 block text-xs text-[#7a7060]">
                  {master.is_active ? 'Active' : 'Inactive'}
                </span>
              </th>
              {master.days.map(day => (
                <td key={`${master.id}-${day.date}`} className="p-2 align-top">
                  <AdminScheduleCell master={master} day={day} onClick={onCellClick} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
