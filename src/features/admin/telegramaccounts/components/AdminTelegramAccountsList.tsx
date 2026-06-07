import type { AdminTelegramAccount } from '../types'
import AdminTelegramAccountCard from './AdminTelegramAccountCard'

type AdminTelegramAccountsListProps = {
  accounts: AdminTelegramAccount[]
  togglingAccountId: number | null
  onEdit: (account: AdminTelegramAccount) => void
  onToggle: (account: AdminTelegramAccount) => void
}

export default function AdminTelegramAccountsList({
  accounts,
  togglingAccountId,
  onEdit,
  onToggle,
}: AdminTelegramAccountsListProps) {
  if (accounts.length === 0) {
    return (
      <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
        No Telegram accounts found
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {accounts.map(account => (
        <AdminTelegramAccountCard
          key={account.id}
          account={account}
          isToggling={togglingAccountId === account.id}
          onEdit={onEdit}
          onToggle={onToggle}
        />
      ))}
    </div>
  )
}
