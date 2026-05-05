import { useRef, useEffect } from 'react'
import Footer from '../components/layout/Footer'
import BookingProgress from '../features/booking/components/BookingProgress'
import ServiceSelect from '../features/booking/components/ServiceSelect'
import DateTimePicker from '../features/booking/components/DateTimePicker'
import MasterSelect from '../features/booking/components/MasterSelect'
import PaymentForm from '../features/booking/components/PaymentForm'
import { useBookingStore } from '../features/booking/hooks/useBookingStore'

const revealStyle = (visible: boolean): React.CSSProperties => ({
  maxHeight: visible ? '2000px' : '0',
  opacity: visible ? 1 : 0,
  overflow: 'hidden',
  transition: 'max-height 0.6s ease, opacity 0.5s ease',
  scrollMarginTop: '24px',
})

export default function BookingPage() {
  const { step, service, date, time, master, setService, setDateTime, setMaster } = useBookingStore()

  const step2Ref = useRef<HTMLDivElement>(null)
  const step3Ref = useRef<HTMLDivElement>(null)
  const step4Ref = useRef<HTMLDivElement>(null)

  const prevStep = useRef(step)
  useEffect(() => {
    if (step > prevStep.current) {
      const map: Record<number, React.RefObject<HTMLDivElement | null>> = {
        2: step2Ref,
        3: step3Ref,
        4: step4Ref,
      }
      const ref = map[step]
      if (ref?.current) {
        const el = ref.current
        // Small delay lets the CSS transition start before scrolling
        setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }), 120)
      }
    }
    prevStep.current = step
  }, [step])

  return (
    <div style={{ background: '#0f0f0f', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '60px 48px 80px' }}>
        {/* Page header */}
        <div style={{ textAlign: 'center', marginBottom: '52px' }}>
          <p style={{ fontSize: '10px', letterSpacing: '5px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '16px' }}>
            Online booking
          </p>
          <h1 style={{ fontSize: '42px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif' }}>
            Reserve your seat
          </h1>
          <div style={{ width: '1px', height: '32px', background: '#2a2218', margin: '28px auto 0' }} />
        </div>

        <BookingProgress step={step} />

        {/* Step 1 — always visible */}
        <div style={{ marginBottom: '48px' }}>
          <ServiceSelect selected={service} onSelect={setService} />
        </div>

        {/* Step 2 — reveals after service selected */}
        <div ref={step2Ref} style={revealStyle(step >= 2)}>
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
        </div>

        {/* Step 3 — reveals after date+time selected */}
        <div ref={step3Ref} style={revealStyle(step >= 3)}>
          <div style={{ marginBottom: '48px' }}>
            <MasterSelect
              date={date}
              time={time}
              selected={master}
              onSelect={setMaster}
            />
          </div>
        </div>

        {/* Step 4 — reveals after barber selected */}
        <div ref={step4Ref} style={revealStyle(step >= 4)}>
          <PaymentForm service={service} date={date} time={time} master={master} />
        </div>
      </div>

      <Footer />
    </div>
  )
}
