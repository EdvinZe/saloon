export type AdminServicesFilter = 'all' | 'active' | 'inactive'

type AdminServicesToolbarProps = {
  filter: AdminServicesFilter
  onFilterChange: (filter: AdminServicesFilter) => void
  onAddService: () => void
}

const filters: { value: AdminServicesFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
]

export default function AdminServicesToolbar({
  filter,
  onFilterChange,
  onAddService,
}: AdminServicesToolbarProps) {
  return (
    <div className="flex flex-col gap-4 border border-[#2a2218] bg-[#141008] p-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Services</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Manage services, prices and durations</h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex border border-[#2a2218]">
          {filters.map(item => (
            <button
              key={item.value}
              type="button"
              onClick={() => onFilterChange(item.value)}
              className={`px-4 py-2 text-xs uppercase tracking-[0.18em] ${
                filter === item.value
                  ? 'bg-[#c9a84c] text-[#0f0f0f]'
                  : 'bg-[#0f0f0f] text-[#7a7060] hover:text-[#e8e0d0]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onAddService}>
          Add service
        </button>
      </div>
    </div>
  )
}
