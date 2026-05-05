export const WORK_START = '09:00'
export const WORK_END = '20:00'
export const SLOT_STEP_MIN = 30
export const MIN_BOOKING_DURATION_MIN = 60

export function toMinutes(time: string): number {
  const [h, m] = time.split(':').map(Number)
  return h * 60 + m
}

export function minutesToTime(total: number): string {
  const h = Math.floor(total / 60)
  const m = total % 60

  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

export function generateSlotTimes({
  start = WORK_START,
  end = WORK_END,
  stepMin = SLOT_STEP_MIN,
  minDurationMin = MIN_BOOKING_DURATION_MIN,
}: {
  start?: string
  end?: string
  stepMin?: number
  minDurationMin?: number
} = {}): string[] {
  const startMin = toMinutes(start)
  const endMin = toMinutes(end)
  const lastStartMin = endMin - minDurationMin

  const times: string[] = []

  for (let current = startMin; current <= lastStartMin; current += stepMin) {
    times.push(minutesToTime(current))
  }

  return times
}