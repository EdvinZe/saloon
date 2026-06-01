import type { AdminService } from '../types'

type AdminServiceCardProps = {
  service: AdminService
  isToggling: boolean
  onEdit: (service: AdminService) => void
  onToggle: (service: AdminService) => void
}

function formatPrice(priceCents: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'EUR',
  }).format(priceCents / 100)
}

export default function AdminServiceCard({
  service,
  isToggling,
  onEdit,
  onToggle,
}: AdminServiceCardProps) {
  return (
    <article className="border border-[#2a2218] bg-[#141008] p-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl text-[#e8e0d0]">{service.name}</h2>
            <span
              className={`border px-2 py-1 text-[11px] uppercase tracking-[0.16em] ${
                service.is_active
                  ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
                  : 'border-zinc-700 bg-zinc-900/70 text-zinc-400'
              }`}
            >
              {service.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="mt-2 text-sm text-[#7a7060]">{service.description || 'No description'}</p>
        </div>

        <div className="flex gap-2">
          <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={() => onEdit(service)}>
            Edit
          </button>
          <button
            type="button"
            className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
            onClick={() => onToggle(service)}
            disabled={isToggling}
          >
            {service.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-4">
        <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">Price</dt>
          <dd className="mt-1 text-lg text-[#e8e0d0]">{formatPrice(service.price_cents)}</dd>
        </div>
        <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">Duration</dt>
          <dd className="mt-1 text-lg text-[#e8e0d0]">{service.duration_minutes} min</dd>
        </div>
        <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">Cleanup</dt>
          <dd className="mt-1 text-lg text-[#e8e0d0]">{service.cleanup_time_minutes} min</dd>
        </div>
        <div className="border border-[#211a12] bg-[#0f0f0f] p-3">
          <dt className="text-xs uppercase tracking-[0.16em] text-[#7a7060]">Total</dt>
          <dd className="mt-1 text-lg text-[#e8e0d0]">{service.total_duration_minutes} min</dd>
        </div>
      </dl>
    </article>
  )
}
