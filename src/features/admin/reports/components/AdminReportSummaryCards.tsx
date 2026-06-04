import type { AdminReportSummary } from '../types'
import { formatCents } from '../utils/money'

type AdminReportSummaryCardsProps = {
  report: AdminReportSummary
}

export default function AdminReportSummaryCards({ report }: AdminReportSummaryCardsProps) {
  const cards = [
    { label: 'Total bookings', value: report.total_bookings },
    { label: 'Confirmed', value: report.confirmed_count },
    { label: 'Completed', value: report.completed_count },
    { label: 'Cancelled', value: report.cancelled_count },
    { label: 'No-show', value: report.no_show_count },
    {
      label: 'Paid deposits',
      value: formatCents(report.paid_deposits_cents, report.currency),
    },
    {
      label: 'Refunded deposits',
      value: formatCents(report.refunded_deposits_cents, report.currency),
    },
    {
      label: 'Net deposits',
      value: formatCents(report.net_deposits_cents, report.currency),
    },
  ]

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(card => (
        <div key={card.label} className="border border-[#2a2218] bg-[#141008] p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">{card.label}</p>
          <p className="mt-3 text-2xl text-[#e8e0d0]">{card.value}</p>
        </div>
      ))}
    </div>
  )
}
