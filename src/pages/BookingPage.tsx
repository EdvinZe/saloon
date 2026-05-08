import Footer from '../components/layout/Footer'
import BookingPageHeader from '../features/booking/components/BookingPageHeader'
import BookingProgress from '../features/booking/components/BookingProgress'
import BookingStepSection from '../features/booking/components/BookingStepSection'
import ServiceSelect from '../features/booking/components/ServiceSelect'
import DateTimePicker from '../features/booking/components/DateTimePicker'
import MasterSelect from '../features/booking/components/MasterSelect'
import PaymentForm from '../features/booking/components/PaymentForm'
import { useBookingStore } from '../features/booking/hooks/useBookingStore'
import { useBookingStepScroll } from '../features/booking/hooks/useBookingStepScroll'


export default function BookingPage() {
  const { step, service, date, time, master, setService, setDateTime, setMaster } = useBookingStore()
  const { step2Ref, step3Ref, step4Ref } = useBookingStepScroll(step)

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px 48px 80px' }}>
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
            <MasterSelect
              date={date}
              time={time}
              selected={master}
              onSelect={setMaster}
            />
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
