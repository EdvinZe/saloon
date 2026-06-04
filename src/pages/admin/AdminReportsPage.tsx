import { useMemo, useState } from 'react'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import AdminReportDailyBreakdown from '../../features/admin/reports/components/AdminReportDailyBreakdown'
import AdminReportMasterBreakdown from '../../features/admin/reports/components/AdminReportMasterBreakdown'
import AdminReportsToolbar, {
  type ReportPresetKey,
} from '../../features/admin/reports/components/AdminReportsToolbar'
import AdminReportServiceBreakdown from '../../features/admin/reports/components/AdminReportServiceBreakdown'
import AdminReportSummaryCards from '../../features/admin/reports/components/AdminReportSummaryCards'
import { useAdminReportSummary } from '../../features/admin/reports/hooks/useAdminReportSummary'
import {
  getLastMonthRange,
  getLastWeekRange,
  getThisMonthRange,
  getThisWeekRange,
  getThisYearRange,
  getTodayDateString,
  getTodayRange,
  getYesterdayRange,
  type ReportDateRange,
} from '../../features/admin/reports/utils/reportPresets'
import { useAdminMasters } from '../../features/admin/masters/hooks/useAdminMasters'

const presetRanges: Record<ReportPresetKey, () => ReportDateRange> = {
  today: getTodayRange,
  yesterday: getYesterdayRange,
  this_week: getThisWeekRange,
  last_week: getLastWeekRange,
  this_month: getThisMonthRange,
  last_month: getLastMonthRange,
  this_year: getThisYearRange,
}

function getErrorMessage(error: unknown, fallback: string) {
  if (
    typeof error === 'object' &&
    error !== null &&
    'responseBody' in error &&
    typeof error.responseBody === 'object' &&
    error.responseBody !== null &&
    'detail' in error.responseBody &&
    typeof error.responseBody.detail === 'string'
  ) {
    return error.responseBody.detail
  }

  return fallback
}

export default function AdminReportsPage() {
  const initialRange = useMemo(() => getTodayRange(), [])
  const [fromDate, setFromDate] = useState(initialRange.fromDate)
  const [toDate, setToDate] = useState(initialRange.toDate)
  const [masterId, setMasterId] = useState<number | 'all'>('all')
  const [activePreset, setActivePreset] = useState<ReportPresetKey | 'custom'>('today')

  const today = getTodayDateString()
  const validationError = useMemo(() => {
    if (!fromDate || !toDate) return null
    if (toDate > today) return 'Future reports are not available'
    if (fromDate > toDate) return 'Invalid report date range'
    return null
  }, [fromDate, toDate, today])

  const reportQuery = useAdminReportSummary(
    validationError ? '' : fromDate,
    validationError ? '' : toDate,
    masterId === 'all' ? null : masterId,
  )
  const mastersQuery = useAdminMasters()

  const selectPreset = (preset: ReportPresetKey) => {
    const range = presetRanges[preset]()
    setFromDate(range.fromDate)
    setToDate(range.toDate)
    setActivePreset(preset)
  }

  const updateFromDate = (value: string) => {
    setFromDate(value)
    setActivePreset('custom')
  }

  const updateToDate = (value: string) => {
    setToDate(value)
    setActivePreset('custom')
  }

  const report = reportQuery.data
  const hasNoBookings = Boolean(report && report.total_bookings === 0)

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminReportsToolbar
          fromDate={fromDate}
          toDate={toDate}
          masterId={masterId}
          masters={mastersQuery.data ?? []}
          activePreset={activePreset}
          onPresetSelect={selectPreset}
          onFromDateChange={updateFromDate}
          onToDateChange={updateToDate}
          onMasterChange={setMasterId}
        />

        {validationError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {validationError}
          </div>
        ) : null}

        {reportQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading report summary...
          </div>
        ) : null}

        {reportQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(reportQuery.error, 'Could not load report summary.')}
          </div>
        ) : null}

        {report ? (
          <>
            <AdminReportSummaryCards report={report} />

            {hasNoBookings ? (
              <div className="border border-[#2a2218] bg-[#141008] p-5 text-sm text-[#7a7060]">
                No bookings found for this period.
              </div>
            ) : null}

            <AdminReportMasterBreakdown rows={report.by_master} currency={report.currency} />
            <AdminReportServiceBreakdown rows={report.by_service} currency={report.currency} />
            <AdminReportDailyBreakdown rows={report.daily_breakdown} currency={report.currency} />
          </>
        ) : null}

        <div className="sr-only">
          TODO: add CSV and PDF export for admin reports in a future iteration.
        </div>
      </div>
    </AdminLayout>
  )
}
