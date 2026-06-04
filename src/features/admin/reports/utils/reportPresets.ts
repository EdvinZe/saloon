export type ReportDateRange = {
  fromDate: string
  toDate: string
}

function formatLocalDate(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function startOfWeek(date: Date) {
  const result = new Date(date)
  const day = result.getDay()
  const diff = day === 0 ? -6 : 1 - day
  result.setDate(result.getDate() + diff)
  return result
}

function addDays(date: Date, days: number) {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

function makeRange(fromDate: Date, toDate: Date): ReportDateRange {
  const today = new Date()
  const safeToDate = toDate > today ? today : toDate

  return {
    fromDate: formatLocalDate(fromDate),
    toDate: formatLocalDate(safeToDate),
  }
}

export function getTodayRange() {
  const today = new Date()
  return makeRange(today, today)
}

export function getYesterdayRange() {
  const yesterday = addDays(new Date(), -1)
  return makeRange(yesterday, yesterday)
}

export function getThisWeekRange() {
  const today = new Date()
  return makeRange(startOfWeek(today), today)
}

export function getLastWeekRange() {
  const thisWeekStart = startOfWeek(new Date())
  const lastWeekStart = addDays(thisWeekStart, -7)
  const lastWeekEnd = addDays(thisWeekStart, -1)
  return makeRange(lastWeekStart, lastWeekEnd)
}

export function getThisMonthRange() {
  const today = new Date()
  return makeRange(new Date(today.getFullYear(), today.getMonth(), 1), today)
}

export function getLastMonthRange() {
  const today = new Date()
  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1)
  const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0)
  return makeRange(lastMonthStart, lastMonthEnd)
}

export function getThisYearRange() {
  const today = new Date()
  return makeRange(new Date(today.getFullYear(), 0, 1), today)
}

export function getTodayDateString() {
  return formatLocalDate(new Date())
}
