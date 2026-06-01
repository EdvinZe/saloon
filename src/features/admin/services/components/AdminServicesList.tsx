import type { AdminService } from '../types'
import AdminServiceCard from './AdminServiceCard'

type AdminServicesListProps = {
  services: AdminService[]
  togglingServiceId: number | null
  onEdit: (service: AdminService) => void
  onToggle: (service: AdminService) => void
}

export default function AdminServicesList({
  services,
  togglingServiceId,
  onEdit,
  onToggle,
}: AdminServicesListProps) {
  if (services.length === 0) {
    return (
      <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
        No services found
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {services.map(service => (
        <AdminServiceCard
          key={service.id}
          service={service}
          isToggling={togglingServiceId === service.id}
          onEdit={onEdit}
          onToggle={onToggle}
        />
      ))}
    </div>
  )
}
