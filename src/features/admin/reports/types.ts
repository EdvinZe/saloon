export type AdminReportMasterSummary = {
  master_id: number
  master_name: string
  total_bookings: number
  confirmed_count: number
  completed_count: number
  cancelled_count: number
  no_show_count: number
  paid_deposits_cents: number
  refunded_deposits_cents: number
  net_deposits_cents: number
}

export type AdminReportServiceSummary = {
  service_id: number
  service_name: string
  total_bookings: number
  completed_count: number
  cancelled_count: number
  no_show_count: number
  paid_deposits_cents: number
  refunded_deposits_cents: number
  net_deposits_cents: number
}

export type AdminReportDailySummary = {
  date: string
  total_bookings: number
  completed_count: number
  cancelled_count: number
  no_show_count: number
  paid_deposits_cents: number
  refunded_deposits_cents: number
  net_deposits_cents: number
}

export type AdminReportSummary = {
  from_date: string
  to_date: string
  master_id: number | null
  total_bookings: number
  confirmed_count: number
  completed_count: number
  cancelled_count: number
  no_show_count: number
  paid_deposits_cents: number
  refunded_deposits_cents: number
  net_deposits_cents: number
  currency: string
  by_master: AdminReportMasterSummary[]
  by_service: AdminReportServiceSummary[]
  daily_breakdown: AdminReportDailySummary[]
}

export type AdminReportSummaryParams = {
  fromDate: string
  toDate: string
  masterId?: number | null
}
