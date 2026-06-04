import type { AdminReportMasterSummary } from '../types'
import { formatCents } from '../utils/money'

type AdminReportMasterBreakdownProps = {
  rows: AdminReportMasterSummary[]
  currency: string
}

export default function AdminReportMasterBreakdown({
  rows,
  currency,
}: AdminReportMasterBreakdownProps) {
  if (rows.length === 0) return null

  return (
    <section className="border border-[#2a2218] bg-[#141008] p-4">
      <h2 className="text-lg text-[#e8e0d0]">By master</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-left text-sm">
          <thead className="text-xs uppercase tracking-[0.14em] text-[#7a7060]">
            <tr className="border-b border-[#2a2218]">
              <th className="py-3 pr-3 font-normal">Master</th>
              <th className="py-3 pr-3 font-normal">Total</th>
              <th className="py-3 pr-3 font-normal">Confirmed</th>
              <th className="py-3 pr-3 font-normal">Completed</th>
              <th className="py-3 pr-3 font-normal">Cancelled</th>
              <th className="py-3 pr-3 font-normal">No-show</th>
              <th className="py-3 pr-3 font-normal">Net deposits</th>
            </tr>
          </thead>
          <tbody className="text-[#e8e0d0]">
            {rows.map(row => (
              <tr key={row.master_id} className="border-b border-[#2a2218]/70 last:border-0">
                <td className="py-3 pr-3">{row.master_name || `Master #${row.master_id}`}</td>
                <td className="py-3 pr-3">{row.total_bookings}</td>
                <td className="py-3 pr-3">{row.confirmed_count}</td>
                <td className="py-3 pr-3">{row.completed_count}</td>
                <td className="py-3 pr-3">{row.cancelled_count}</td>
                <td className="py-3 pr-3">{row.no_show_count}</td>
                <td className="py-3 pr-3">{formatCents(row.net_deposits_cents, currency)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
