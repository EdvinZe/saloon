import { useState } from 'react'
import type { AdminMaster } from '../../masters/types'
import type {
  AdminTelegramAccount,
  AdminTelegramAccountCreateInput,
  AdminTelegramAccountRole,
  AdminTelegramAccountUpdateInput,
} from '../types'

type AdminTelegramAccountFormModalProps = {
  account?: AdminTelegramAccount | null
  masters: AdminMaster[]
  isSaving: boolean
  errorMessage?: string | null
  onClose: () => void
  onCreate: (payload: AdminTelegramAccountCreateInput) => void
  onUpdate: (id: number, payload: AdminTelegramAccountUpdateInput) => void
}

export default function AdminTelegramAccountFormModal({
  account,
  masters,
  isSaving,
  errorMessage,
  onClose,
  onCreate,
  onUpdate,
}: AdminTelegramAccountFormModalProps) {
  const isEditing = Boolean(account)
  const [telegramId, setTelegramId] = useState(String(account?.telegram_id ?? ''))
  const [role, setRole] = useState<AdminTelegramAccountRole>(account?.role ?? 'manager')
  const [firstName, setFirstName] = useState(account?.first_name ?? '')
  const [lastName, setLastName] = useState(account?.last_name ?? '')
  const [masterId, setMasterId] = useState(account?.master_id ? String(account.master_id) : '')
  const [isActive, setIsActive] = useState(account?.is_active ?? true)
  const [validationError, setValidationError] = useState<string | null>(null)

  const submitForm = () => {
    const normalizedTelegramId = telegramId.trim()
    const parsedTelegramId = Number(normalizedTelegramId)
    const normalizedFirstName = firstName.trim()
    const normalizedLastName = lastName.trim()
    const parsedMasterId = masterId ? Number(masterId) : null

    if (!normalizedTelegramId) {
      setValidationError('Telegram ID is required')
      return
    }

    if (!/^\d+$/.test(normalizedTelegramId)) {
      setValidationError('Telegram ID must contain only digits.')
      return
    }

    if (!normalizedFirstName) {
      setValidationError('First name is required')
      return
    }

    if (role === 'barber' && parsedMasterId === null) {
      setValidationError('Master is required for barber accounts')
      return
    }

    const payload = {
      telegram_id: parsedTelegramId,
      role,
      first_name: normalizedFirstName,
      last_name: normalizedLastName || null,
      master_id: role === 'barber' ? parsedMasterId : null,
      is_active: isActive,
    }

    setValidationError(null)

    if (account) {
      onUpdate(account.id, payload)
      return
    }

    onCreate(payload)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <form
        className="w-full max-w-xl border border-[#2a2218] bg-[#141008] p-5 shadow-2xl"
        onSubmit={event => {
          event.preventDefault()
          submitForm()
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#c9a84c]">
              {isEditing ? 'Edit Telegram account' : 'Create Telegram account'}
            </p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">
              {isEditing ? account?.first_name : 'New account'}
            </h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm text-[#7a7060]">
            Telegram ID
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={telegramId}
              onChange={event => setTelegramId(event.target.value)}
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
              required
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Role
              <select
                value={role}
                onChange={event => {
                  const nextRole = event.target.value as AdminTelegramAccountRole
                  setRole(nextRole)
                  if (nextRole === 'manager') setMasterId('')
                }}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              >
                <option value="manager">Manager</option>
                <option value="barber">Barber</option>
              </select>
            </label>

            <label className="grid gap-2 text-sm text-[#7a7060]">
              Master
              <select
                value={masterId}
                onChange={event => setMasterId(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0] disabled:opacity-60"
                disabled={role === 'manager'}
                required={role === 'barber'}
              >
                <option value="">Select master</option>
                {masters.map(master => (
                  <option key={master.id} value={master.id}>
                    {master.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              First name
              <input
                value={firstName}
                onChange={event => setFirstName(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Last name
              <input
                value={lastName}
                onChange={event => setLastName(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
              />
            </label>
          </div>

          <label className="flex items-center gap-3 text-sm text-[#e8e0d0]">
            <input
              type="checkbox"
              checked={isActive}
              onChange={event => setIsActive(event.target.checked)}
              className="h-4 w-4 accent-[#c9a84c]"
            />
            Active
          </label>
        </div>

        {validationError || errorMessage ? (
          <p className="mt-4 text-sm text-rose-300">{validationError ?? errorMessage}</p>
        ) : null}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="px-4 py-2 text-sm text-[#7a7060]" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn-gold px-5 py-2 text-xs" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  )
}
