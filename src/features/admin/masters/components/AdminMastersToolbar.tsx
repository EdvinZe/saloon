import {
  adminFilterButtonActiveClassName,
  adminFilterButtonBaseClassName,
  adminFilterButtonInactiveClassName,
  adminFilterGroupClassName,
  adminToolbarActionsClassName,
  adminToolbarClassName,
} from '../../layout/adminStyles'

export type AdminMastersFilter = 'all' | 'active' | 'inactive'

type AdminMastersToolbarProps = {
  filter: AdminMastersFilter
  onFilterChange: (filter: AdminMastersFilter) => void
  onAddMaster: () => void
}

const filters: { value: AdminMastersFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
]

export default function AdminMastersToolbar({
  filter,
  onFilterChange,
  onAddMaster,
}: AdminMastersToolbarProps) {
  return (
    <div className={adminToolbarClassName}>
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Masters</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Manage barbers, availability and services</h1>
      </div>

      <div className={adminToolbarActionsClassName}>
        <div className={adminFilterGroupClassName}>
          {filters.map(item => (
            <button
              key={item.value}
              type="button"
              onClick={() => onFilterChange(item.value)}
              className={`${adminFilterButtonBaseClassName} ${
                filter === item.value
                  ? adminFilterButtonActiveClassName
                  : adminFilterButtonInactiveClassName
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onAddMaster}>
          Add master
        </button>
      </div>
    </div>
  )
}
