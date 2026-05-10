import { useState } from 'react'
import type { Service, Master } from '../../../shared/data/mockData'
import BookingSummary from './BookingSummary'
import { useBookingStore } from '../hooks/useBookingStore'
import { useBookingConfig } from '../../bookingconfig/hooks/useBookingConfig'

interface Props {
  service: Service | null
  date: string | null
  time: string | null
  master: Master | null
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  background: '#0f0f0f',
  border: '1px solid #2a2218',
  color: '#e8e0d0',
  padding: '13px 16px',
  fontSize: '14px',
  fontFamily: 'sans-serif',
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.2s',
}

const labelStyle: React.CSSProperties = {
  fontSize: '10px',
  letterSpacing: '2px',
  color: '#5a5040',
  textTransform: 'uppercase',
  fontFamily: 'sans-serif',
  display: 'block',
  marginBottom: '8px',
}

const sectionHeadStyle: React.CSSProperties = {
  fontSize: '10px',
  color: '#7a7060',
  fontFamily: 'sans-serif',
  letterSpacing: '3px',
  textTransform: 'uppercase',
  marginBottom: '20px',
  paddingBottom: '12px',
  borderBottom: '1px solid #1a1810',
}

export default function PaymentForm({ service, date, time, master }: Props) {
  const { clientName, clientPhone, setClientName, setClientPhone } = useBookingStore()
  const { data: bookingConfig } = useBookingConfig()
  const depositAmount = bookingConfig?.depositAmount ?? 10
  const currency = bookingConfig?.currency ?? 'EUR'
  const currencySymbol = currency === 'EUR' ? '€' : currency
  // Tracks which mock card field appears "focused"
  const [cardFocus, setCardFocus] = useState<string | null>(null)

  const mockFieldStyle = (field: string): React.CSSProperties => ({
    ...inputStyle,
    color: cardFocus === field ? '#7a7060' : '#3a3020',
    borderColor: cardFocus === field ? '#c9a84c' : '#2a2218',
    cursor: 'text',
    userSelect: 'none',
  })

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <div style={{ marginBottom: '28px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
          Step 4
        </p>
        <h2 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400 }}>Your details & payment</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1px', background: '#2a2218', alignItems: 'start', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
        {/* Left: form fields */}
        <div style={{ background: '#141008', padding: 'clamp(24px, 6vw, 36px)', minWidth: 0, boxSizing: 'border-box' }}>
          {/* Personal details */}
          <div style={{ marginBottom: '36px' }}>
            <div style={sectionHeadStyle}>Personal details</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
              <div>
                <label style={labelStyle}>Full name</label>
                <input
                  type="text"
                  value={clientName}
                  onChange={e => setClientName(e.target.value)}
                  placeholder="Your name"
                  style={inputStyle}
                  onFocus={e => (e.currentTarget.style.borderColor = '#c9a84c')}
                  onBlur={e => (e.currentTarget.style.borderColor = '#2a2218')}
                />
              </div>
              <div>
                <label style={labelStyle}>Phone number</label>
                <input
                  type="tel"
                  value={clientPhone}
                  onChange={e => setClientPhone(e.target.value)}
                  placeholder="+370 ..."
                  style={inputStyle}
                  onFocus={e => (e.currentTarget.style.borderColor = '#c9a84c')}
                  onBlur={e => (e.currentTarget.style.borderColor = '#2a2218')}
                />
              </div>
            </div>
          </div>

          {/* Mock Stripe card fields */}
          <div>
            <div style={sectionHeadStyle}>Card details</div>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>Card number</label>
              <div
                style={{ ...mockFieldStyle('card'), display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                onClick={() => setCardFocus(f => f === 'card' ? null : 'card')}
              >
                <span>•••• •••• •••• ••••</span>
                <span style={{ fontSize: '11px', color: '#3a3020', letterSpacing: '1px' }}>VISA / MC</span>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
              <div>
                <label style={labelStyle}>Expiry</label>
                <div
                  style={mockFieldStyle('exp')}
                  onClick={() => setCardFocus(f => f === 'exp' ? null : 'exp')}
                >
                  MM / YY
                </div>
              </div>
              <div>
                <label style={labelStyle}>CVC</label>
                <div
                  style={mockFieldStyle('cvc')}
                  onClick={() => setCardFocus(f => f === 'cvc' ? null : 'cvc')}
                >
                  •••
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: summary + CTA */}
        <div style={{ background: '#0f0f0f', padding: 'clamp(24px, 6vw, 36px)', minWidth: 0, boxSizing: 'border-box' }}>
          <BookingSummary service={service} date={date} time={time} master={master} depositAmount={depositAmount} currencySymbol={currencySymbol} />

          <button
            style={{
              width: '100%',
              marginTop: '20px',
              padding: '18px 24px',
              background: 'transparent',
              border: '1px solid #c9a84c',
              color: '#c9a84c',
              fontSize: '11px',
              letterSpacing: '3px',
              textTransform: 'uppercase',
              cursor: 'pointer',
              fontFamily: 'Georgia, serif',
              fontWeight: 400,
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'rgba(201,168,76,0.08)'
              e.currentTarget.style.boxShadow = '0 0 20px rgba(201,168,76,0.2)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            Confirm & pay {currencySymbol}{depositAmount} deposit →
          </button>

          <p style={{ fontSize: '11px', color: '#3a3020', fontFamily: 'sans-serif', textAlign: 'center', marginTop: '14px', lineHeight: 1.7 }}>
            Deposit is held — not charged until<br />your visit is confirmed
          </p>
        </div>
      </div>
    </div>
  )
}
