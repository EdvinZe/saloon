import { useMemo, useState } from 'react'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import AdminServiceFormModal from '../../features/admin/services/components/AdminServiceFormModal'
import AdminServicesList from '../../features/admin/services/components/AdminServicesList'
import AdminServicesToolbar, {
  type AdminServicesFilter,
} from '../../features/admin/services/components/AdminServicesToolbar'
import { useAdminServices } from '../../features/admin/services/hooks/useAdminServices'
import { useCreateAdminService } from '../../features/admin/services/hooks/useCreateAdminService'
import { useToggleAdminService } from '../../features/admin/services/hooks/useToggleAdminService'
import { useUpdateAdminService } from '../../features/admin/services/hooks/useUpdateAdminService'
import type {
  AdminService,
  AdminServiceCreateInput,
  AdminServiceUpdateInput,
} from '../../features/admin/services/types'

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
    if (Array.isArray(detail)) return 'Please check the service form fields'
  }

  return fallback
}

export default function AdminServicesPage() {
  const [filter, setFilter] = useState<AdminServicesFilter>('all')
  const [editingService, setEditingService] = useState<AdminService | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [togglingServiceId, setTogglingServiceId] = useState<number | null>(null)

  const servicesQuery = useAdminServices()
  const createMutation = useCreateAdminService()
  const updateMutation = useUpdateAdminService()
  const toggleMutation = useToggleAdminService()

  const filteredServices = useMemo(() => {
    const services = servicesQuery.data ?? []

    if (filter === 'active') {
      return services.filter(service => service.is_active)
    }

    if (filter === 'inactive') {
      return services.filter(service => !service.is_active)
    }

    return services
  }, [filter, servicesQuery.data])

  const isSaving = createMutation.isPending || updateMutation.isPending
  const formError = createMutation.isError
    ? getErrorMessage(createMutation.error, 'Failed to create service')
    : updateMutation.isError
      ? getErrorMessage(updateMutation.error, 'Failed to update service')
      : null

  const openCreateModal = () => {
    createMutation.reset()
    updateMutation.reset()
    setEditingService(null)
    setIsFormOpen(true)
  }

  const openEditModal = (service: AdminService) => {
    createMutation.reset()
    updateMutation.reset()
    setEditingService(service)
    setIsFormOpen(true)
  }

  const closeFormModal = () => {
    setIsFormOpen(false)
    setEditingService(null)
  }

  const createService = (payload: AdminServiceCreateInput) => {
    createMutation.mutate(payload, {
      onSuccess: closeFormModal,
    })
  }

  const updateService = (id: number, payload: AdminServiceUpdateInput) => {
    updateMutation.mutate({ id, payload }, {
      onSuccess: closeFormModal,
    })
  }

  const toggleService = (service: AdminService) => {
    setTogglingServiceId(service.id)
    toggleMutation.mutate(
      { id: service.id, nextIsActive: !service.is_active },
      {
        onSettled: () => setTogglingServiceId(null),
      },
    )
  }

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminServicesToolbar
          filter={filter}
          onFilterChange={setFilter}
          onAddService={openCreateModal}
        />

        {servicesQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading services...
          </div>
        ) : null}

        {servicesQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(servicesQuery.error, 'Failed to load services')}
          </div>
        ) : null}

        {toggleMutation.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(toggleMutation.error, 'Failed to update service status')}
          </div>
        ) : null}

        {servicesQuery.data ? (
          <AdminServicesList
            services={filteredServices}
            togglingServiceId={togglingServiceId}
            onEdit={openEditModal}
            onToggle={toggleService}
          />
        ) : null}
      </div>

      {isFormOpen ? (
        <AdminServiceFormModal
          service={editingService}
          isSaving={isSaving}
          errorMessage={formError}
          onClose={closeFormModal}
          onCreate={createService}
          onUpdate={updateService}
        />
      ) : null}
    </AdminLayout>
  )
}
