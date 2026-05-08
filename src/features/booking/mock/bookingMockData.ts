export interface MockBusyBooking {
  startTime: string
  durationMin: number
}

export const MOCK_BUSY_BOOKINGS: MockBusyBooking[] = [
  { startTime: '09:00', durationMin: 60 },
  { startTime: '10:30', durationMin: 60 },
  { startTime: '13:00', durationMin: 60 },
  { startTime: '15:30', durationMin: 60 },
  { startTime: '17:00', durationMin: 60 },
]

export interface MockExistingBooking {
  masterId: string
  date: string
  startTime: string  // 'HH:MM'
  durationMin: number
}

const d = new Date()
export const TODAY_STR = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

// Alex busy at 11:00 today — triggers Step 3 (master select) in reschedule flow
// Michael busy at 14:00 today — demonstrates multi-master filtering
export const MOCK_EXISTING: MockExistingBooking[] = [
  { masterId: '1', date: TODAY_STR, startTime: '11:00', durationMin: 45 },
  { masterId: '2', date: TODAY_STR, startTime: '14:00', durationMin: 30 },
]
