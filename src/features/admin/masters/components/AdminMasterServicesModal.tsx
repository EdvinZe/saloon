import { useState } from 'react'
import { useAdminServices } from '../../services/hooks/useAdminServices'
import type { AdminMaster } from '../types'

type AdminMasterServicesModalProps = {
  master: AdminMaster
  isSaving: boolean
  errorMessage?: string | null
  onClose: () => void
  onSave: (masterId: number, serviceIds: number[]) => void
}

function formatPrice(priceCents: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'EUR',
  }).format(priceCents / 100)
}

export default function AdminMasterServicesModal({
  master,
  isSaving,
  errorMessage,
  onClose,
  onSave,
}: AdminMasterServicesModalProps) {
  const servicesQuery = useAdminServices()
  const [selectedServiceIds, setSelectedServiceIds] = useState<number[]>(
    master.services.map(service => service.id),
  )

  const toggleService = (serviceId: number) => {
    setSelectedServiceIds(current => (
      current.includes(serviceId)
        ? current.filter(id => id !== serviceId)
        : [...current, serviceId]
    ))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <form
        className="flex max-h-[90vh] w-full max-w-2xl flex-col border border-[#2a2218] bg-[#141008] p-5 shadow-2xl"
        onSubmit={event => {
          event.preventDefault()
          onSave(master.id, selectedServiceIds)
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#c9a84c]">Assign services</p>
            <h2 className="mt-2 text-xl text-[#e8e0d0]">{master.name}</h2>
          </div>
          <button type="button" className="text-2xl leading-none text-[#7a7060]" onClick={onClose}>
            x
          </button>
        </div>

        <div className="mt-5 min-h-0 overflow-y-auto pr-1">
          {servicesQuery.isLoading ? (
            <div className="border border-[#2a2218] bg-[#0f0f0f] p-5 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
              Loading services...
            </div>
          ) : null}

          {servicesQuery.isError ? (
            <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
              Failed to load services
            </div>
          ) : null}

          {servicesQuery.data ? (
            <div className="grid gap-2">
              {servicesQuery.data.map(service => {
                const isSelected = selectedServiceIds.includes(service.id)

                return (
                  <label
                    key={service.id}
                    className={`flex cursor-pointer items-start gap-3 border p-3 ${
                      isSelected
                        ? 'border-[#c9a84c] bg-[#c9a84c]/10'
                        : 'border-[#2a2218] bg-[#0f0f0f]'
                    } ${service.is_active ? '' : 'opacity-65'}`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleService(service.id)}
                      className="mt-1 h-4 w-4 accent-[#c9a84c]"
                    />
                    <span className="min-w-0 flex-1">
                      <span className="flex flex-wrap items-center gap-2">
                        <span className="text-sm text-[#e8e0d0]">{service.name}</span>
                        {!service.is_active ? (
                          <span className="border border-zinc-700 bg-zinc-900/70 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-zinc-400">
                            Inactive
                          </span>
                        ) : null}
                      </span>
                      <span className="mt-1 block text-xs text-[#7a7060]">
                        {formatPrice(service.price_cents)} · {service.duration_minutes} min + {service.cleanup_time_minutes} min cleanup
                      </span>
                    </span>
                  </label>
                )
              })}
            </div>
          ) : null}
        </div>

        {errorMessage ? <p className="mt-4 text-sm text-rose-300">{errorMessage}</p> : null}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="px-4 py-2 text-sm text-[#7a7060]" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn-gold px-5 py-2 text-xs" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save services'}
          </button>
        </div>
      </form>
    </div>
  )
}
