import { useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import Footer from '../components/layout/Footer'
import BookingPageHeader from '../features/booking/components/BookingPageHeader'
import BookingProgress from '../features/booking/components/BookingProgress'
import BookingStepSection from '../features/booking/components/BookingStepSection'
import ServiceSelect from '../features/booking/components/ServiceSelect'
import DateTimePicker from '../features/booking/components/DateTimePicker'
import MasterSelect from '../features/booking/components/MasterSelect'
import PaymentForm from '../features/booking/components/PaymentForm'
import { useBookingStore } from '../features/booking/hooks/useBookingStore'
import { useAvailableMasters } from '../features/booking/hooks/useAvailableMasters'
import { useBookingServices } from '../features/booking/hooks/useBookingServices'
import { useBookingStepScroll } from '../features/booking/hooks/useBookingStepScroll'


export default function BookingPage() {
  const { step, service, date, time, master, setService, setDateTime, setMaster } = useBookingStore()
  const { step2Ref, step3Ref, step4Ref } = useBookingStepScroll(step)
  const [searchParams] = useSearchParams()
  const prefillAppliedRef = useRef({
    service: false,
    dateTime: false,
    master: false,
  })
  const serviceIdParam = parsePositiveInt(searchParams.get('serviceId'))
  const masterIdParam = parsePositiveInt(searchParams.get('masterId'))
  const prefillDate = searchParams.get('date')
  const prefillTime = searchParams.get('time')
  const { data: services = [] } = useBookingServices()
  const { data: availableMasters = [] } = useAvailableMasters(
    prefillDate,
    prefillTime,
    serviceIdParam,
  )

  useEffect(() => {
    if (prefillAppliedRef.current.service || serviceIdParam === null || services.length === 0) {
      return
    }

    const prefilledService = services.find(item => item.id === serviceIdParam)
    if (!prefilledService) return

    setService(prefilledService)
    prefillAppliedRef.current.service = true
  }, [serviceIdParam, services, setService])

  useEffect(() => {
    if (
      prefillAppliedRef.current.dateTime ||
      !service ||
      !prefillDate ||
      !prefillTime ||
      serviceIdParam !== service.id
    ) {
      return
    }

    setDateTime(prefillDate, prefillTime)
    prefillAppliedRef.current.dateTime = true
  }, [prefillDate, prefillTime, service, serviceIdParam, setDateTime])

  useEffect(() => {
    if (
      prefillAppliedRef.current.master ||
      masterIdParam === null ||
      !service ||
      !date ||
      !time ||
      availableMasters.length === 0
    ) {
      return
    }

    const prefilledMaster = availableMasters.find(item => item.id === masterIdParam)
    if (!prefilledMaster) return

    setMaster(prefilledMaster)
    prefillAppliedRef.current.master = true
  }, [availableMasters, date, masterIdParam, service, setMaster, time])

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh', overflowX: 'hidden' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px clamp(20px, 5vw, 48px) 80px', width: '100%', boxSizing: 'border-box' }}>
        <BookingPageHeader />

        <BookingProgress step={step} />

        {/* Step 1 — always visible */}
        <div style={{ marginBottom: '48px' }}>
          <ServiceSelect selected={service} onSelect={setService} />
        </div>

        {/* Step 2 — reveals after service selected */}
        <BookingStepSection ref={step2Ref} visible={step >= 2}>
          <div style={{ marginBottom: '48px' }}>
            {service && (
              <DateTimePicker
                service={service}
                selectedDate={date}
                selectedTime={time}
                onSelect={setDateTime}
              />
            )}
          </div>
        </BookingStepSection>

        {/* Step 3 — reveals after date+time selected */}
        <BookingStepSection ref={step3Ref} visible={step >= 3}>
          <div style={{ marginBottom: '48px' }}>
            {service && (
              <MasterSelect
                service={service}
                date={date}
                time={time}
                selected={master}
                onSelect={setMaster}
              />
            )}
          </div>
        </BookingStepSection>

        {/* Step 4 — reveals after barber selected */}
        <BookingStepSection ref={step4Ref} visible={step >= 4}>
          <PaymentForm service={service} date={date} time={time} master={master} />
        </BookingStepSection>
      </div>

      <Footer />
    </div>
  )
}

function parsePositiveInt(value: string | null): number | null {
  if (!value) return null

  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}
