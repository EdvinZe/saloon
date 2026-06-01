import type { AdminMaster } from '../types'
import AdminMasterCard from './AdminMasterCard'

type AdminMastersListProps = {
  masters: AdminMaster[]
  togglingMasterId: number | null
  onEdit: (master: AdminMaster) => void
  onEditServices: (master: AdminMaster) => void
  onToggle: (master: AdminMaster) => void
}

export default function AdminMastersList({
  masters,
  togglingMasterId,
  onEdit,
  onEditServices,
  onToggle,
}: AdminMastersListProps) {
  if (masters.length === 0) {
    return (
      <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
        No masters found
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {masters.map(master => (
        <AdminMasterCard
          key={master.id}
          master={master}
          isToggling={togglingMasterId === master.id}
          onEdit={onEdit}
          onEditServices={onEditServices}
          onToggle={onToggle}
        />
      ))}
    </div>
  )
}
