export type AdminTelegramAccountsStatusFilter = 'all' | 'active' | 'inactive'
export type AdminTelegramAccountsRoleFilter = 'all' | 'manager' | 'barber'

type AdminTelegramAccountsToolbarProps = {
  statusFilter: AdminTelegramAccountsStatusFilter
  roleFilter: AdminTelegramAccountsRoleFilter
  onStatusFilterChange: (filter: AdminTelegramAccountsStatusFilter) => void
  onRoleFilterChange: (filter: AdminTelegramAccountsRoleFilter) => void
  onAddAccount: () => void
}

const statusFilters: { value: AdminTelegramAccountsStatusFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
]

const roleFilters: { value: AdminTelegramAccountsRoleFilter; label: string }[] = [
  { value: 'all', label: 'All roles' },
  { value: 'manager', label: 'Manager' },
  { value: 'barber', label: 'Barber' },
]

export default function AdminTelegramAccountsToolbar({
  statusFilter,
  roleFilter,
  onStatusFilterChange,
  onRoleFilterChange,
  onAddAccount,
}: AdminTelegramAccountsToolbarProps) {
  return (
    <div className="flex flex-col gap-4 border border-[#2a2218] bg-[#141008] p-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-[#c9a84c]">Telegram Accounts</p>
        <h1 className="mt-2 text-2xl text-[#e8e0d0]">Manage who can use the Telegram bot</h1>
        <p className="mt-2 max-w-3xl text-sm text-[#7a7060]">
          Bot integration is currently configured through environment variables. These accounts
          are prepared for future bot access management.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex border border-[#2a2218]">
          {statusFilters.map(item => (
            <button
              key={item.value}
              type="button"
              onClick={() => onStatusFilterChange(item.value)}
              className={`px-4 py-2 text-xs uppercase tracking-[0.18em] ${
                statusFilter === item.value
                  ? 'bg-[#c9a84c] text-[#0f0f0f]'
                  : 'bg-[#0f0f0f] text-[#7a7060] hover:text-[#e8e0d0]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        <select
          value={roleFilter}
          onChange={event => onRoleFilterChange(event.target.value as AdminTelegramAccountsRoleFilter)}
          className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0]"
        >
          {roleFilters.map(item => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>

        <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={onAddAccount}>
          Add account
        </button>
      </div>
    </div>
  )
}
