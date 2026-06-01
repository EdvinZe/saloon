export type AdminScheduleStatus =
  | 'working'
  | 'extra_day'
  | 'day_off'
  | 'vacation'
  | 'sick'
  | 'other'
  | 'not_set'

export type AdminEditableScheduleStatus = Exclude<AdminScheduleStatus, 'not_set'>

export type AdminScheduleDay = {
  date: string
  shift_id: number | null
  status: AdminScheduleStatus
  start_time: string | null
  end_time: string | null
  note: string | null
}

export type AdminScheduleMaster = {
  id: number
  name: string
  is_active: boolean
  days: AdminScheduleDay[]
}

export type AdminScheduleResponse = {
  from_date: string
  to_date: string
  days: string[]
  masters: AdminScheduleMaster[]
}

export type AdminScheduleDayUpsert = {
  master_id: number
  date: string
  status: AdminEditableScheduleStatus
  start_time?: string | null
  end_time?: string | null
  note?: string | null
}

export type AdminScheduleRangeUpsert = {
  master_id: number
  from_date: string
  to_date: string
  status: AdminEditableScheduleStatus
  start_time?: string | null
  end_time?: string | null
  note?: string | null
}

export type AdminScheduleRangeResponse = {
  success: boolean
  message: string
  updated_count: number
}
