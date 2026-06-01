export type AdminBookingStatus = 'confirmed' | 'cancelled' | 'completed' | 'no_show'

export type AdminDepositStatus = 'paid' | 'refunded' | 'retained' | 'unpaid' | 'pending' | string

export type AdminBooking = {
  id: number
  booking_code: string | null
  service_id: number
  master_id: number
  customer_first_name: string
  customer_last_name: string
  customer_phone: string
  customer_email: string
  start_at: string
  end_at: string
  status: AdminBookingStatus
  deposit_status: AdminDepositStatus
  source: string
  deposit_amount_cents: number
  currency: string
  stripe_payment_intent_id: string | null
  stripe_checkout_session_id: string | null
  created_at: string
  updated_at: string
  service_name: string | null
  master_name: string | null
}

export type AdminBookingListParams = {
  date?: string | null
  status?: AdminBookingStatus | null
  masterId?: number | null
  serviceId?: number | null
}

export type AdminBookingActionResponse = {
  success: boolean
  message: string
  booking: AdminBooking
}
