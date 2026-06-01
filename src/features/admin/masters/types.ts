export type AdminMasterService = {
  id: number
  name: string
  price_cents: number
  duration_minutes: number
  cleanup_time_minutes: number
  is_active: boolean
}

export type AdminMaster = {
  id: number
  first_name: string
  last_name: string
  name: string
  role: string
  bio: string
  initials: string
  birth_date: string | null
  is_active: boolean
  sort_order: number
  services: AdminMasterService[]
  created_at: string
  updated_at: string
}

export type AdminMasterCreateInput = {
  first_name: string
  last_name: string
  role: string
  bio?: string
  initials: string
  birth_date?: string | null
  is_active?: boolean
  sort_order?: number
  service_ids?: number[]
}

export type AdminMasterUpdateInput = Partial<AdminMasterCreateInput>

export type AdminMasterServicesUpdateInput = {
  service_ids: number[]
}
