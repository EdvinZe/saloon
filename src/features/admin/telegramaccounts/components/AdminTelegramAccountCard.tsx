import type { AdminTelegramAccount } from '../types'

type AdminTelegramAccountCardProps = {
  account: AdminTelegramAccount
  isToggling: boolean
  onEdit: (account: AdminTelegramAccount) => void
  onToggle: (account: AdminTelegramAccount) => void
}

function getAccountName(account: AdminTelegramAccount) {
  return [account.first_name, account.last_name].filter(Boolean).join(' ')
}

export default function AdminTelegramAccountCard({
  account,
  isToggling,
  onEdit,
  onToggle,
}: AdminTelegramAccountCardProps) {
  const roleLabel = account.role === 'manager' ? 'Manager' : 'Barber'

  return (
    <article className={`border border-[#2a2218] bg-[#141008] p-4 ${account.is_active ? '' : 'opacity-70'}`}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <div>
              <h2 className="text-xl text-[#e8e0d0]">{getAccountName(account)}</h2>
              <p className="mt-1 text-sm text-[#7a7060]">Telegram ID: {account.telegram_id}</p>
            </div>

            <span className="border border-[#c9a84c]/40 bg-[#c9a84c]/10 px-2 py-1 text-[11px] uppercase tracking-[0.16em] text-[#f2d985]">
              {roleLabel}
            </span>

            <span
              className={`border px-2 py-1 text-[11px] uppercase tracking-[0.16em] ${
                account.is_active
                  ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
                  : 'border-zinc-700 bg-zinc-900/70 text-zinc-400'
              }`}
            >
              {account.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          {account.role === 'barber' ? (
            <p className="mt-3 text-sm text-[#7a7060]">
              Master: {account.master_name ?? (account.master_id ? `#${account.master_id}` : 'Not assigned')}
            </p>
          ) : null}
        </div>

        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-gold px-4 py-2 text-xs" onClick={() => onEdit(account)}>
            Edit
          </button>
          <button
            type="button"
            className="border border-[#2a2218] px-4 py-2 text-xs uppercase tracking-[0.18em] text-[#e8e0d0] hover:border-[#c9a84c]"
            onClick={() => onToggle(account)}
            disabled={isToggling}
          >
            {account.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </div>
      </div>
    </article>
  )
}
