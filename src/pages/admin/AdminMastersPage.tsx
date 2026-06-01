import { useMemo, useState } from 'react'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import AdminMasterFormModal from '../../features/admin/masters/components/AdminMasterFormModal'
import AdminMasterServicesModal from '../../features/admin/masters/components/AdminMasterServicesModal'
import AdminMastersList from '../../features/admin/masters/components/AdminMastersList'
import AdminMastersToolbar, {
  type AdminMastersFilter,
} from '../../features/admin/masters/components/AdminMastersToolbar'
import { useAdminMasters } from '../../features/admin/masters/hooks/useAdminMasters'
import { useCreateAdminMaster } from '../../features/admin/masters/hooks/useCreateAdminMaster'
import { useToggleAdminMaster } from '../../features/admin/masters/hooks/useToggleAdminMaster'
import { useUpdateAdminMaster } from '../../features/admin/masters/hooks/useUpdateAdminMaster'
import { useUpdateAdminMasterServices } from '../../features/admin/masters/hooks/useUpdateAdminMasterServices'
import type {
  AdminMaster,
  AdminMasterCreateInput,
  AdminMasterUpdateInput,
} from '../../features/admin/masters/types'

function getErrorMessage(error: unknown, fallback: string) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'responseBody' in error &&
    typeof error.responseBody === 'object' &&
    error.responseBody !== null &&
    'detail' in error.responseBody
  ) {
    const detail = error.responseBody.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return 'Please check the master form fields'
  }

  return fallback
}

export default function AdminMastersPage() {
  const [filter, setFilter] = useState<AdminMastersFilter>('all')
  const [editingMaster, setEditingMaster] = useState<AdminMaster | null>(null)
  const [servicesMaster, setServicesMaster] = useState<AdminMaster | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [togglingMasterId, setTogglingMasterId] = useState<number | null>(null)

  const mastersQuery = useAdminMasters()
  const createMutation = useCreateAdminMaster()
  const updateMutation = useUpdateAdminMaster()
  const toggleMutation = useToggleAdminMaster()
  const servicesMutation = useUpdateAdminMasterServices()

  const filteredMasters = useMemo(() => {
    const masters = mastersQuery.data ?? []

    if (filter === 'active') {
      return masters.filter(master => master.is_active)
    }

    if (filter === 'inactive') {
      return masters.filter(master => !master.is_active)
    }

    return masters
  }, [filter, mastersQuery.data])

  const isSaving = createMutation.isPending || updateMutation.isPending
  const formError = createMutation.isError
    ? getErrorMessage(createMutation.error, 'Failed to create master')
    : updateMutation.isError
      ? getErrorMessage(updateMutation.error, 'Failed to update master')
      : null

  const openCreateModal = () => {
    createMutation.reset()
    updateMutation.reset()
    setEditingMaster(null)
    setIsFormOpen(true)
  }

  const openEditModal = (master: AdminMaster) => {
    createMutation.reset()
    updateMutation.reset()
    setEditingMaster(master)
    setIsFormOpen(true)
  }

  const closeFormModal = () => {
    setIsFormOpen(false)
    setEditingMaster(null)
  }

  const createMaster = (payload: AdminMasterCreateInput) => {
    createMutation.mutate(payload, {
      onSuccess: closeFormModal,
    })
  }

  const updateMaster = (id: number, payload: AdminMasterUpdateInput) => {
    updateMutation.mutate({ id, payload }, {
      onSuccess: closeFormModal,
    })
  }

  const toggleMaster = (master: AdminMaster) => {
    setTogglingMasterId(master.id)
    toggleMutation.mutate(
      { id: master.id, nextIsActive: !master.is_active },
      {
        onSettled: () => setTogglingMasterId(null),
      },
    )
  }

  const saveMasterServices = (masterId: number, serviceIds: number[]) => {
    servicesMutation.mutate(
      { id: masterId, serviceIds },
      {
        onSuccess: () => setServicesMaster(null),
      },
    )
  }

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminMastersToolbar
          filter={filter}
          onFilterChange={setFilter}
          onAddMaster={openCreateModal}
        />

        {mastersQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading masters...
          </div>
        ) : null}

        {mastersQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(mastersQuery.error, 'Failed to load masters')}
          </div>
        ) : null}

        {toggleMutation.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(toggleMutation.error, 'Failed to update master status')}
          </div>
        ) : null}

        {mastersQuery.data ? (
          <AdminMastersList
            masters={filteredMasters}
            togglingMasterId={togglingMasterId}
            onEdit={openEditModal}
            onEditServices={master => {
              servicesMutation.reset()
              setServicesMaster(master)
            }}
            onToggle={toggleMaster}
          />
        ) : null}
      </div>

      {isFormOpen ? (
        <AdminMasterFormModal
          master={editingMaster}
          isSaving={isSaving}
          errorMessage={formError}
          onClose={closeFormModal}
          onCreate={createMaster}
          onUpdate={updateMaster}
        />
      ) : null}

      {servicesMaster ? (
        <AdminMasterServicesModal
          master={servicesMaster}
          isSaving={servicesMutation.isPending}
          errorMessage={servicesMutation.isError ? getErrorMessage(servicesMutation.error, 'Failed to update master services') : null}
          onClose={() => setServicesMaster(null)}
          onSave={saveMasterServices}
        />
      ) : null}
    </AdminLayout>
  )
}
