import { useEffect, useState } from 'react'
import type { AdminMaster, AdminMasterCreateInput, AdminMasterUpdateInput } from '../types'

type AdminMasterFormModalProps = {
  master?: AdminMaster | null
  isSaving: boolean
  errorMessage?: string | null
  onClose: () => void
  onCreate: (payload: AdminMasterCreateInput) => void
  onUpdate: (id: number, payload: AdminMasterUpdateInput) => void
}

export default function AdminMasterFormModal({
  master,
  isSaving,
  errorMessage,
  onClose,
  onCreate,
  onUpdate,
}: AdminMasterFormModalProps) {
  const isEditing = Boolean(master)
  const [firstName, setFirstName] = useState(master?.first_name ?? '')
  const [lastName, setLastName] = useState(master?.last_name ?? '')
  const [role, setRole] = useState(master?.role ?? '')
  const [bio, setBio] = useState(master?.bio ?? '')
  const [initials, setInitials] = useState(master?.initials ?? '')
  const [birthDate, setBirthDate] = useState(master?.birth_date ?? '')
  const [isActive, setIsActive] = useState(master?.is_active ?? true)
  const [sortOrder, setSortOrder] = useState(String(master?.sort_order ?? 0))
  const [validationError, setValidationError] = useState<string | null>(null)

  useEffect(() => {
    setFirstName(master?.first_name ?? '')
    setLastName(master?.last_name ?? '')
    setRole(master?.role ?? '')
    setBio(master?.bio ?? '')
    setInitials(master?.initials ?? '')
    setBirthDate(master?.birth_date ?? '')
    setIsActive(master?.is_active ?? true)
    setSortOrder(String(master?.sort_order ?? 0))
    setValidationError(null)
  }, [master])

  const submitForm = () => {
    const normalizedFirstName = firstName.trim()
    const normalizedLastName = lastName.trim()
    const normalizedRole = role.trim()
    const normalizedInitials = initials.trim()
    const order = Number(sortOrder)

    if (!normalizedFirstName || !normalizedLastName) {
      setValidationError('First and last name are required')
      return
    }

    if (!normalizedRole) {
      setValidationError('Role is required')
      return
    }

    if (!normalizedInitials) {
      setValidationError('Initials are required')
      return
    }

    if (!Number.isFinite(order)) {
      setValidationError('Sort order must be a number')
      return
    }

    const payload = {
      first_name: normalizedFirstName,
      last_name: normalizedLastName,
      role: normalizedRole,
      bio: bio.trim(),
      initials: normalizedInitials,
      birth_date: birthDate || null,
      is_active: isActive,
      sort_order: order,
    }

    setValidationError(null)

    if (master) {
      onUpdate(master.id, payload)
      return
    }

    onCreate({ ...payload, service_ids: [] })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <form
        className="max-h-[90vh] w-full max-w-xl overflow-y-auto border border-[#2a2218] bg-[#141008] p-5 shadow-2xl"
        onSubmit={event => {
          event.preventDefault()
          submitForm()
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#c9a84c]">
              {isEditing ? 'Edit master' : 'Create master'}
            </p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">
              {isEditing ? master?.name : 'New master'}
            </h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 grid gap-4">
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
                required
              />
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Role
              <input
                value={role}
                onChange={event => setRole(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Initials
              <input
                value={initials}
                onChange={event => setInitials(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
          </div>

          <label className="grid gap-2 text-sm text-[#7a7060]">
            Bio
            <textarea
              value={bio}
              onChange={event => setBio(event.target.value)}
              className="min-h-24 border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Birth date
              <input
                type="date"
                value={birthDate}
                onChange={event => setBirthDate(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
              />
            </label>
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Sort order
              <input
                type="number"
                step="1"
                value={sortOrder}
                onChange={event => setSortOrder(event.target.value)}
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
