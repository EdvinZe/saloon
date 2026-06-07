import { useMemo, useState } from 'react'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import { useAdminMasters } from '../../features/admin/masters/hooks/useAdminMasters'
import AdminTelegramAccountFormModal from '../../features/admin/telegramaccounts/components/AdminTelegramAccountFormModal'
import AdminTelegramAccountsList from '../../features/admin/telegramaccounts/components/AdminTelegramAccountsList'
import AdminTelegramAccountsToolbar, {
  type AdminTelegramAccountsRoleFilter,
  type AdminTelegramAccountsStatusFilter,
} from '../../features/admin/telegramaccounts/components/AdminTelegramAccountsToolbar'
import { useAdminTelegramAccounts } from '../../features/admin/telegramaccounts/hooks/useAdminTelegramAccounts'
import { useCreateAdminTelegramAccount } from '../../features/admin/telegramaccounts/hooks/useCreateAdminTelegramAccount'
import { useToggleAdminTelegramAccount } from '../../features/admin/telegramaccounts/hooks/useToggleAdminTelegramAccount'
import { useUpdateAdminTelegramAccount } from '../../features/admin/telegramaccounts/hooks/useUpdateAdminTelegramAccount'
import type {
  AdminTelegramAccount,
  AdminTelegramAccountCreateInput,
  AdminTelegramAccountUpdateInput,
} from '../../features/admin/telegramaccounts/types'

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
    if (Array.isArray(detail)) return 'Please check the Telegram account form fields'
  }

  return fallback
}

export default function AdminTelegramAccountsPage() {
  const [statusFilter, setStatusFilter] = useState<AdminTelegramAccountsStatusFilter>('all')
  const [roleFilter, setRoleFilter] = useState<AdminTelegramAccountsRoleFilter>('all')
  const [editingAccount, setEditingAccount] = useState<AdminTelegramAccount | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [togglingAccountId, setTogglingAccountId] = useState<number | null>(null)

  const accountsQuery = useAdminTelegramAccounts()
  const mastersQuery = useAdminMasters()
  const createMutation = useCreateAdminTelegramAccount()
  const updateMutation = useUpdateAdminTelegramAccount()
  const toggleMutation = useToggleAdminTelegramAccount()

  const filteredAccounts = useMemo(() => {
    let accounts = accountsQuery.data ?? []

    if (statusFilter === 'active') {
      accounts = accounts.filter(account => account.is_active)
    } else if (statusFilter === 'inactive') {
      accounts = accounts.filter(account => !account.is_active)
    }

    if (roleFilter !== 'all') {
      accounts = accounts.filter(account => account.role === roleFilter)
    }

    return accounts
  }, [accountsQuery.data, roleFilter, statusFilter])

  const isSaving = createMutation.isPending || updateMutation.isPending
  const formError = createMutation.isError
    ? getErrorMessage(createMutation.error, 'Failed to create Telegram account')
    : updateMutation.isError
      ? getErrorMessage(updateMutation.error, 'Failed to update Telegram account')
      : null

  const openCreateModal = () => {
    createMutation.reset()
    updateMutation.reset()
    setEditingAccount(null)
    setIsFormOpen(true)
  }

  const openEditModal = (account: AdminTelegramAccount) => {
    createMutation.reset()
    updateMutation.reset()
    setEditingAccount(account)
    setIsFormOpen(true)
  }

  const closeFormModal = () => {
    setIsFormOpen(false)
    setEditingAccount(null)
  }

  const createAccount = (payload: AdminTelegramAccountCreateInput) => {
    createMutation.mutate(payload, {
      onSuccess: closeFormModal,
    })
  }

  const updateAccount = (id: number, payload: AdminTelegramAccountUpdateInput) => {
    updateMutation.mutate({ id, payload }, {
      onSuccess: closeFormModal,
    })
  }

  const toggleAccount = (account: AdminTelegramAccount) => {
    setTogglingAccountId(account.id)
    toggleMutation.mutate(
      { id: account.id, nextIsActive: !account.is_active },
      {
        onSettled: () => setTogglingAccountId(null),
      },
    )
  }

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminTelegramAccountsToolbar
          statusFilter={statusFilter}
          roleFilter={roleFilter}
          onStatusFilterChange={setStatusFilter}
          onRoleFilterChange={setRoleFilter}
          onAddAccount={openCreateModal}
        />

        {accountsQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading Telegram accounts...
          </div>
        ) : null}

        {accountsQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(accountsQuery.error, 'Failed to load Telegram accounts')}
          </div>
        ) : null}

        {toggleMutation.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(toggleMutation.error, 'Failed to update Telegram account status')}
          </div>
        ) : null}

        {accountsQuery.data ? (
          <AdminTelegramAccountsList
            accounts={filteredAccounts}
            togglingAccountId={togglingAccountId}
            onEdit={openEditModal}
            onToggle={toggleAccount}
          />
        ) : null}
      </div>

      {isFormOpen ? (
        <AdminTelegramAccountFormModal
          account={editingAccount}
          masters={mastersQuery.data ?? []}
          isSaving={isSaving}
          errorMessage={formError}
          onClose={closeFormModal}
          onCreate={createAccount}
          onUpdate={updateAccount}
        />
      ) : null}
    </AdminLayout>
  )
}
