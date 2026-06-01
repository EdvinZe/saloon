export type AdminService = {
  id: number
  name: string
  description: string
  price_cents: number
  duration_minutes: number
  cleanup_time_minutes: number
  total_duration_minutes: number
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export type AdminServiceCreateInput = {
  name: string
  description?: string
  price_cents: number
  duration_minutes: number
  cleanup_time_minutes: number
  is_active?: boolean
  sort_order?: number
}

export type AdminServiceUpdateInput = Partial<AdminServiceCreateInput>
