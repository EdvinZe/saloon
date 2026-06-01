import type { AdminMaster } from '../types'

type AdminMasterCardProps = {
  master: AdminMaster
  isToggling: boolean
  onEdit: (master: AdminMaster) => void
  onEditServices: (master: AdminMaster) => void
  onToggle: (master: AdminMaster) => void
}

export default function AdminMasterCard({
  master,
  isToggling,
  onEdit,
  onEditServices,
  onToggle,
}: AdminMasterCardProps) {
  return (
    <article className={`border border-[#2a2218] bg-[#141008] p-4 ${master.is_active ? '' : 'opacity-70'}`}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center border border-[#2a2218] bg-[#0f0f0f] text-sm uppercase tracking-[0.16em] text-[#c9a84c]">
              {master.initials}
            </div>
            <div>
              <h2 className="text-xl text-[#e8e0d0]">{master.name}</h2>
              <p className="text-sm text-[#7a7060]">{master.role}</p>
            </div>
            <span
              className={`border px-2 py-1 text-[11px] uppercase tracking-[0.16em] ${
                master.is_active
                  ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
                  : 'border-zinc-700 bg-zinc-900/70 text-zinc-400'
              }`}
            >
              {master.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <p className="mt-3 text-sm text-[#7a7060]">{master.bio || 'No bio'}</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={() => onEdit(master)}>
            Edit
          </button>
          <button
            type="button"
            className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
            onClick={() => onEditServices(master)}
          >
            Services
          </button>
          <button
            type="button"
            className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
            onClick={() => onToggle(master)}
            disabled={isToggling}
          >
            {master.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {master.services.length ? master.services.map(service => (
          <span
            key={service.id}
            className={`border px-3 py-1 text-xs ${
              service.is_active
                ? 'border-[#c9a84c]/40 bg-[#c9a84c]/10 text-[#f2d985]'
                : 'border-zinc-700 bg-zinc-900/70 text-zinc-400'
            }`}
          >
            {service.name}
          </span>
        )) : (
          <span className="border border-[#2a2218] px-3 py-1 text-xs text-[#7a7060]">
            No services assigned
          </span>
        )}
      </div>
    </article>
  )
}
