import { useState } from 'react'
import type { AdminService, AdminServiceCreateInput, AdminServiceUpdateInput } from '../types'

type AdminServiceFormModalProps = {
  service?: AdminService | null
  isSaving: boolean
  errorMessage?: string | null
  onClose: () => void
  onCreate: (payload: AdminServiceCreateInput) => void
  onUpdate: (id: number, payload: AdminServiceUpdateInput) => void
}

function centsToEuroString(priceCents: number) {
  return (priceCents / 100).toFixed(2)
}

function euroStringToCents(value: string) {
  return Math.round(Number(value || 0) * 100)
}

export default function AdminServiceFormModal({
  service,
  isSaving,
  errorMessage,
  onClose,
  onCreate,
  onUpdate,
}: AdminServiceFormModalProps) {
  const isEditing = Boolean(service)
  const [name, setName] = useState(service?.name ?? '')
  const [description, setDescription] = useState(service?.description ?? '')
  const [price, setPrice] = useState(service ? centsToEuroString(service.price_cents) : '0.00')
  const [durationMinutes, setDurationMinutes] = useState(String(service?.duration_minutes ?? 30))
  const [cleanupMinutes, setCleanupMinutes] = useState(String(service?.cleanup_time_minutes ?? 15))
  const [isActive, setIsActive] = useState(service?.is_active ?? true)
  const [sortOrder, setSortOrder] = useState(String(service?.sort_order ?? 0))
  const [validationError, setValidationError] = useState<string | null>(null)

  const submitForm = () => {
    const normalizedName = name.trim()
    const priceCents = euroStringToCents(price)
    const duration = Number(durationMinutes)
    const cleanup = Number(cleanupMinutes)
    const order = Number(sortOrder)

    if (!normalizedName) {
      setValidationError('Name is required')
      return
    }

    if (!Number.isFinite(priceCents) || priceCents < 0) {
      setValidationError('Price must be zero or greater')
      return
    }

    if (!Number.isFinite(duration) || duration <= 0) {
      setValidationError('Duration must be greater than zero')
      return
    }

    if (!Number.isFinite(cleanup) || cleanup < 0) {
      setValidationError('Cleanup must be zero or greater')
      return
    }

    if (!Number.isFinite(order)) {
      setValidationError('Sort order must be a number')
      return
    }

    const payload = {
      name: normalizedName,
      description: description.trim(),
      price_cents: priceCents,
      duration_minutes: duration,
      cleanup_time_minutes: cleanup,
      is_active: isActive,
      sort_order: order,
    }

    setValidationError(null)

    if (service) {
      onUpdate(service.id, payload)
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
              {isEditing ? 'Edit service' : 'Create service'}
            </p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">
              {isEditing ? service?.name : 'New service'}
            </h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm text-[#7a7060]">
            Name
            <input
              value={name}
              onChange={event => setName(event.target.value)}
              className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
              required
            />
          </label>

          <label className="grid gap-2 text-sm text-[#7a7060]">
            Description
            <textarea
              value={description}
              onChange={event => setDescription(event.target.value)}
              className="min-h-24 border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Price EUR
              <input
                type="number"
                min="0"
                step="0.01"
                value={price}
                onChange={event => setPrice(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
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

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Duration minutes
              <input
                type="number"
                min="1"
                step="1"
                value={durationMinutes}
                onChange={event => setDurationMinutes(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-[#7a7060]">
              Cleanup minutes
              <input
                type="number"
                min="0"
                step="1"
                value={cleanupMinutes}
                onChange={event => setCleanupMinutes(event.target.value)}
                className="border border-[#2a2218] bg-[#0f0f0f] px-3 py-2 text-[#e8e0d0]"
                required
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
