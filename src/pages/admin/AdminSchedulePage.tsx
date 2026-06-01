import { useState } from 'react'
import { addDays, format, startOfWeek } from 'date-fns'
import AdminLayout from '../../features/admin/layout/AdminLayout'
import AdminScheduleDayModal from '../../features/admin/schedule/components/AdminScheduleDayModal'
import AdminScheduleRangeModal from '../../features/admin/schedule/components/AdminScheduleRangeModal'
import AdminScheduleTable from '../../features/admin/schedule/components/AdminScheduleTable'
import AdminScheduleToolbar from '../../features/admin/schedule/components/AdminScheduleToolbar'
import { useAdminSchedule } from '../../features/admin/schedule/hooks/useAdminSchedule'
import { useUpdateAdminScheduleDay } from '../../features/admin/schedule/hooks/useUpdateAdminScheduleDay'
import { useUpdateAdminScheduleRange } from '../../features/admin/schedule/hooks/useUpdateAdminScheduleRange'
import type { AdminScheduleDay, AdminScheduleMaster } from '../../features/admin/schedule/types'

type SelectedScheduleDay = {
  master: AdminScheduleMaster
  day: AdminScheduleDay
}

function getCurrentWeekRange() {
  const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })

  return {
    fromDate: format(weekStart, 'yyyy-MM-dd'),
    toDate: format(addDays(weekStart, 6), 'yyyy-MM-dd'),
  }
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

export default function AdminSchedulePage() {
  const initialRange = getCurrentWeekRange()
  const [fromDate, setFromDate] = useState(initialRange.fromDate)
  const [toDate, setToDate] = useState(initialRange.toDate)
  const [draftFromDate, setDraftFromDate] = useState(initialRange.fromDate)
  const [draftToDate, setDraftToDate] = useState(initialRange.toDate)
  const [selectedDay, setSelectedDay] = useState<SelectedScheduleDay | null>(null)
  const [isRangeModalOpen, setIsRangeModalOpen] = useState(false)

  const scheduleQuery = useAdminSchedule(fromDate, toDate)
  const dayMutation = useUpdateAdminScheduleDay()
  const rangeMutation = useUpdateAdminScheduleRange()
  const hasMasters = Boolean(scheduleQuery.data?.masters.length)

  const moveWeek = (direction: -1 | 1) => {
    const nextFromDate = format(addDays(new Date(`${fromDate}T12:00:00`), direction * 7), 'yyyy-MM-dd')
    const nextToDate = format(addDays(new Date(`${toDate}T12:00:00`), direction * 7), 'yyyy-MM-dd')
    setFromDate(nextFromDate)
    setToDate(nextToDate)
    setDraftFromDate(nextFromDate)
    setDraftToDate(nextToDate)
  }

  const applyThisWeek = () => {
    const nextRange = getCurrentWeekRange()
    setFromDate(nextRange.fromDate)
    setToDate(nextRange.toDate)
    setDraftFromDate(nextRange.fromDate)
    setDraftToDate(nextRange.toDate)
  }

  const applyDraftRange = () => {
    setFromDate(draftFromDate)
    setToDate(draftToDate)
  }

  return (
    <AdminLayout>
      <div className="grid gap-5">
        <AdminScheduleToolbar
          fromDate={fromDate}
          toDate={toDate}
          draftFromDate={draftFromDate}
          draftToDate={draftToDate}
          onDraftFromDateChange={setDraftFromDate}
          onDraftToDateChange={setDraftToDate}
          onApplyRange={applyDraftRange}
          onPreviousWeek={() => moveWeek(-1)}
          onThisWeek={applyThisWeek}
          onNextWeek={() => moveWeek(1)}
          onOpenRangeModal={() => setIsRangeModalOpen(true)}
        />

        {scheduleQuery.isLoading ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            Loading schedule...
          </div>
        ) : null}

        {scheduleQuery.isError ? (
          <div className="border border-rose-500/30 bg-rose-500/10 p-5 text-sm text-rose-200">
            {getErrorMessage(scheduleQuery.error, 'Failed to load schedule')}
          </div>
        ) : null}

        {scheduleQuery.data && !hasMasters ? (
          <div className="border border-[#2a2218] bg-[#141008] p-8 text-center text-sm uppercase tracking-[0.2em] text-[#7a7060]">
            No masters found
          </div>
        ) : null}

        {scheduleQuery.data && hasMasters ? (
          <AdminScheduleTable
            schedule={scheduleQuery.data}
            onCellClick={(master, day) => {
              dayMutation.reset()
              setSelectedDay({ master, day })
            }}
          />
        ) : null}
      </div>

      {selectedDay ? (
        <AdminScheduleDayModal
          selected={selectedDay}
          isSaving={dayMutation.isPending}
          errorMessage={dayMutation.isError ? getErrorMessage(dayMutation.error, 'Failed to save day') : null}
          onClose={() => setSelectedDay(null)}
          onSave={payload => {
            dayMutation.mutate(payload, {
              onSuccess: () => setSelectedDay(null),
            })
          }}
        />
      ) : null}

      {isRangeModalOpen && scheduleQuery.data ? (
        <AdminScheduleRangeModal
          masters={scheduleQuery.data.masters}
          fromDate={fromDate}
          toDate={toDate}
          isSaving={rangeMutation.isPending}
          errorMessage={rangeMutation.isError ? getErrorMessage(rangeMutation.error, 'Failed to save range') : null}
          onClose={() => setIsRangeModalOpen(false)}
          onSave={payload => {
            rangeMutation.mutate(payload, {
              onSuccess: () => setIsRangeModalOpen(false),
            })
          }}
        />
      ) : null}
    </AdminLayout>
  )
}
