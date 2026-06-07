export type AdminTelegramAccountRole = 'manager' | 'barber'

export type AdminTelegramAccount = {
  id: number
  telegram_id: number
  role: AdminTelegramAccountRole
  first_name: string
  last_name: string | null
  master_id: number | null
  master_name?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type AdminTelegramAccountCreateInput = {
  telegram_id: number
  role: AdminTelegramAccountRole
  first_name: string
  last_name?: string | null
  master_id?: number | null
  is_active?: boolean
}

export type AdminTelegramAccountUpdateInput = Partial<AdminTelegramAccountCreateInput>
