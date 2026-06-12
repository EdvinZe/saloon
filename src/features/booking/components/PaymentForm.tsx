import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Elements, PaymentElement, useElements, useStripe } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'
import type { Appearance, StripePaymentElementOptions } from '@stripe/stripe-js'
import type { Master } from '../../masters/api'
import type { Service } from '../../services/api'
import BookingSummary from './BookingSummary'
import { useBookingStore } from '../hooks/useBookingStore'
import { useBookingConfig } from '../../bookingconfig/hooks/useBookingConfig'
import { checkBookingAvailability, createBookingDepositIntent, type BookingCheckPayload } from '../api'

interface Props {
  service: Service | null
  date: string | null
  time: string | null
  master: Master | null
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  backgroundColor: '#080806',
  backgroundImage: 'none',
  border: '1px solid rgba(214, 168, 79, 0.22)',
  color: '#f5f0df',
  padding: '13px 16px',
  fontSize: '14px',
  fontFamily: 'sans-serif',
  outline: 'none',
  boxSizing: 'border-box',
  borderRadius: 0,
  appearance: 'none',
  WebkitAppearance: 'none',
  transition: 'border-color 0.2s, box-shadow 0.2s',
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

const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
const stripePromise = stripePublishableKey ? loadStripe(stripePublishableKey) : null

const stripeAppearance: Appearance = {
  theme: 'night' as const,
  variables: {
    colorPrimary: '#d6a84f',
    colorBackground: '#080806',
    colorText: '#f5f0df',
    colorTextSecondary: '#8f8468',
    colorTextPlaceholder: '#5f563f',
    colorDanger: '#ff6b6b',
    borderRadius: '12px',
    fontFamily: 'Inter, system-ui, sans-serif',
    spacingUnit: '4px',
    focusBoxShadow: '0 0 0 1px rgba(214, 168, 79, 0.35)',
    focusOutline: 'none',
  },
  rules: {
    '.Input': {
      backgroundColor: '#080806',
      border: '1px solid rgba(214, 168, 79, 0.22)',
      color: '#f5f0df',
    },
    '.Input:focus': {
      border: '1px solid rgba(214, 168, 79, 0.75)',
      boxShadow: '0 0 0 1px rgba(214, 168, 79, 0.30), 0 0 18px rgba(214, 168, 79, 0.10)',
    },
    '.Input::placeholder': {
      color: '#5f563f',
    },
    '.Label': {
      color: '#c8b98a',
    },
    '.Tab': {
      backgroundColor: '#080806',
      border: '1px solid rgba(214, 168, 79, 0.18)',
      color: '#f5f0df',
    },
    '.Tab:hover': {
      color: '#d6a84f',
    },
    '.Tab--selected': {
      borderColor: '#d6a84f',
      color: '#d6a84f',
      boxShadow: '0 0 0 1px rgba(214, 168, 79, 0.20)',
    },
    '.Block': {
      backgroundColor: '#080806',
      borderColor: 'rgba(214, 168, 79, 0.18)',
    },
    '.AccordionItem': {
      backgroundColor: '#080806',
      borderColor: 'rgba(214, 168, 79, 0.18)',
    },
    '.AccordionItem--selected': {
      borderColor: 'rgba(214, 168, 79, 0.45)',
    },
  },
}

const SLOT_UNAVAILABLE_MESSAGE = 'This time is no longer available. Please choose another time.'

export default function PaymentForm({ service, date, time, master }: Props) {
  const {
    customerFirstName,
    customerLastName,
    customerPhone,
    customerEmail,
    setCustomerFirstName,
    setCustomerLastName,
    setCustomerPhone,
    setCustomerEmail,
    clearSelectedTimeAndMaster,
  } = useBookingStore()
  const queryClient = useQueryClient()
  const { data: bookingConfig } = useBookingConfig()
  const depositAmount = bookingConfig?.depositAmount ?? 10
  const currency = bookingConfig?.currency ?? 'EUR'
  const currencySymbol = currency === 'EUR' ? '€' : currency
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isChecking, setIsChecking] = useState(false)
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const isStartPaymentDisabled =
    isChecking ||
    Boolean(clientSecret) ||
    !service ||
    !date ||
    !time ||
    !master ||
    !customerFirstName.trim() ||
    !customerLastName.trim() ||
    !customerPhone.trim() ||
    !customerEmail.trim()

  const clearPaymentIntent = () => {
    setClientSecret(null)
    setSuccessMessage(null)
  }

  const refreshAvailabilityAfterSlotConflict = () => {
    clearPaymentIntent()
    setErrorMessage(SLOT_UNAVAILABLE_MESSAGE)
    void Promise.all([
      service && date
        ? queryClient.invalidateQueries({ queryKey: ['booking-slots', date, service.id] })
        : Promise.resolve(),
      service && date && time
        ? queryClient.invalidateQueries({ queryKey: ['available-masters', date, time, service.id] })
        : Promise.resolve(),
      service
        ? queryClient.invalidateQueries({ queryKey: ['nearest-available-slot', service.id] })
        : Promise.resolve(),
    ])
    clearSelectedTimeAndMaster()
  }

  const validateCustomerDetails = () => {
    if (!customerFirstName.trim()) return 'First name is required.'
    if (!customerLastName.trim()) return 'Last name is required.'
    if (!customerPhone.trim()) return 'Phone number is required.'
    if (!customerEmail.trim()) return 'Email is required.'
    if (!customerEmail.includes('@')) return 'Enter a valid email address.'
    return null
  }

  const getBookingPayload = (): BookingCheckPayload | null => {
    if (!service || !master || !date || !time) {
      return null
    }

    return {
      service_id: service.id,
      master_id: master.id,
      date,
      time,
      customer_first_name: customerFirstName.trim(),
      customer_last_name: customerLastName.trim(),
      customer_phone: customerPhone.trim(),
      customer_email: customerEmail.trim(),
    }
  }

  const getErrorStatus = (error: unknown) => {
    if (
      typeof error === 'object' &&
      error !== null &&
      'status' in error &&
      typeof (error as { status?: unknown }).status === 'number'
    ) {
      return (error as { status: number }).status
    }

    if (
      typeof error === 'object' &&
      error !== null &&
      'response' in error &&
      typeof (error as { response?: { status?: unknown } }).response?.status === 'number'
    ) {
      return (error as { response: { status: number } }).response.status
    }

    return null
  }

  const getErrorDetail = (error: unknown) => {
    if (
      typeof error === 'object' &&
      error !== null &&
      'responseBody' in error &&
      typeof (error as { responseBody?: { detail?: unknown } }).responseBody?.detail === 'string'
    ) {
      return (error as { responseBody: { detail: string } }).responseBody.detail
    }

    return null
  }

  const isUnavailableSlotError = (error: unknown) => {
    const status = getErrorStatus(error)
    const detail = getErrorDetail(error)?.toLowerCase() ?? ''
    return (
      status === 409 ||
      (
        status === 400 &&
        (
          detail.includes('slot') ||
          detail.includes('available') ||
          detail.includes('working shift') ||
          detail.includes('past')
        )
      )
    )
  }

  const logPaymentStartError = (error: unknown) => {
    if (typeof error === 'object' && error !== null) {
      const details = error as {
        status?: unknown
        url?: unknown
        responseBody?: unknown
        response?: {
          status?: unknown
          data?: unknown
          config?: { url?: unknown }
        }
      }

      console.error('[BookingPayment] Failed to start payment', {
        status: details.status ?? details.response?.status,
        url: details.url ?? details.response?.config?.url,
        responseBody: details.responseBody ?? details.response?.data,
      }, error)
      return
    }

    console.error('[BookingPayment] Failed to start payment', error)
  }

  const handleStartPayment = async () => {
    if (isChecking || clientSecret) return

    setErrorMessage(null)
    setSuccessMessage(null)

    const validationError = validateCustomerDetails()
    if (validationError) {
      setErrorMessage(validationError)
      return
    }

    if (!stripePublishableKey) {
      console.error('[BookingPayment] Stripe publishable key is not configured')
      setErrorMessage('Payment is temporarily unavailable. Please try again later.')
      return
    }

    const payload = getBookingPayload()
    if (!payload) {
      setErrorMessage('Could not check booking availability. Please try again.')
      return
    }

    setIsChecking(true)

    try {
      const availability = await checkBookingAvailability(payload)
      if (!availability.available) {
        refreshAvailabilityAfterSlotConflict()
        return
      }

      const depositIntent = await createBookingDepositIntent(payload)
      setClientSecret(depositIntent.client_secret)
      setSuccessMessage('Secure payment form is ready.')
    } catch (error) {
      logPaymentStartError(error)
      if (isUnavailableSlotError(error)) {
        refreshAvailabilityAfterSlotConflict()
      } else {
        setErrorMessage('Could not start payment. Please try again.')
      }
    } finally {
      setIsChecking(false)
    }
  }

  return (
    <div style={{ width: '100%', minWidth: 0, background: '#0b0a07' }}>
      <style>
        {`
          .payment-form-input {
            background-color: #080806 !important;
            color: #f5f0df !important;
            caret-color: #d6a84f;
            border: 1px solid rgba(214, 168, 79, 0.22);
            outline: none;
            transition: border-color 160ms ease, box-shadow 160ms ease, background-color 160ms ease;
          }

          .payment-form-input:focus {
            background-color: #080806 !important;
            color: #f5f0df !important;
            border-color: rgba(214, 168, 79, 0.75);
            box-shadow:
              0 0 0 1px rgba(214, 168, 79, 0.30),
              0 0 18px rgba(214, 168, 79, 0.12);
          }

          .payment-form-input::placeholder {
            color: #5f563f;
            opacity: 1;
          }

          .payment-form-input::selection {
            background: rgba(214, 168, 79, 0.35);
            color: #fff7df;
          }

          .payment-form-input::-moz-selection {
            background: rgba(214, 168, 79, 0.35);
            color: #fff7df;
          }

          .payment-form-input:-webkit-autofill,
          .payment-form-input:-webkit-autofill:hover,
          .payment-form-input:-webkit-autofill:focus,
          .payment-form-input:-webkit-autofill:active {
            -webkit-text-fill-color: #f5f0df !important;
            caret-color: #d6a84f !important;
            -webkit-box-shadow: 0 0 0 1000px #080806 inset !important;
            box-shadow: 0 0 0 1000px #080806 inset !important;
            border: 1px solid rgba(214, 168, 79, 0.55) !important;
            transition: background-color 9999s ease-in-out 0s;
          }
        `}
      </style>
      <div style={{ marginBottom: '28px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
          Step 4
        </p>
        <h2 style={{ fontSize: '28px', color: '#e8e0d0', fontWeight: 400 }}>Your details & payment</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1px', background: '#211a11', alignItems: 'stretch', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
        {/* Left: form fields */}
        <div style={{ background: '#100d08', padding: 'clamp(24px, 6vw, 36px)', minWidth: 0, boxSizing: 'border-box' }}>
          {/* Personal details */}
          <div style={{ marginBottom: '36px' }}>
            <div style={sectionHeadStyle}>Personal details</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
              <div>
                <label style={labelStyle}>First name</label>
                <input
                  type="text"
                  value={customerFirstName}
                  onChange={e => {
                    clearPaymentIntent()
                    setCustomerFirstName(e.target.value)
                  }}
                  placeholder="John"
                  autoComplete="given-name"
                  className="payment-form-input"
                  style={inputStyle}
                  onFocus={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.75)'
                    e.currentTarget.style.boxShadow = '0 0 0 1px rgba(214, 168, 79, 0.30), 0 0 18px rgba(214, 168, 79, 0.10)'
                  }}
                  onBlur={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.22)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                />
              </div>
              <div>
                <label style={labelStyle}>Last name</label>
                <input
                  type="text"
                  value={customerLastName}
                  onChange={e => {
                    clearPaymentIntent()
                    setCustomerLastName(e.target.value)
                  }}
                  placeholder="Smith"
                  autoComplete="family-name"
                  className="payment-form-input"
                  style={inputStyle}
                  onFocus={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.75)'
                    e.currentTarget.style.boxShadow = '0 0 0 1px rgba(214, 168, 79, 0.30), 0 0 18px rgba(214, 168, 79, 0.10)'
                  }}
                  onBlur={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.22)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                />
              </div>
              <div>
                <label style={labelStyle}>Phone number</label>
                <input
                  type="tel"
                  value={customerPhone}
                  onChange={e => {
                    clearPaymentIntent()
                    setCustomerPhone(e.target.value)
                  }}
                  placeholder="+370 ..."
                  autoComplete="tel"
                  className="payment-form-input"
                  style={inputStyle}
                  onFocus={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.75)'
                    e.currentTarget.style.boxShadow = '0 0 0 1px rgba(214, 168, 79, 0.30), 0 0 18px rgba(214, 168, 79, 0.10)'
                  }}
                  onBlur={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.22)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                />
              </div>
              <div>
                <label style={labelStyle}>Email</label>
                <input
                  type="email"
                  value={customerEmail}
                  onChange={e => {
                    clearPaymentIntent()
                    setCustomerEmail(e.target.value)
                  }}
                  placeholder="john@example.com"
                  autoComplete="email"
                  className="payment-form-input"
                  style={inputStyle}
                  onFocus={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.75)'
                    e.currentTarget.style.boxShadow = '0 0 0 1px rgba(214, 168, 79, 0.30), 0 0 18px rgba(214, 168, 79, 0.10)'
                  }}
                  onBlur={e => {
                    e.currentTarget.style.backgroundColor = '#080806'
                    e.currentTarget.style.borderColor = 'rgba(214, 168, 79, 0.22)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                />
              </div>
            </div>
          </div>

          <div>
            <div style={sectionHeadStyle}>Card details</div>
            <div
              style={{
                border: clientSecret ? '1px solid rgba(214, 168, 79, 0.18)' : '1px dashed rgba(214, 168, 79, 0.2)',
                background: '#080806',
                minHeight: clientSecret ? 'auto' : '112px',
                display: clientSecret ? 'block' : 'flex',
                alignItems: clientSecret ? undefined : 'center',
                justifyContent: clientSecret ? undefined : 'center',
                padding: '20px',
                boxSizing: 'border-box',
              }}
            >
              {clientSecret ? (
                <Elements
                  stripe={stripePromise}
                  options={{ clientSecret, appearance: stripeAppearance }}
                >
                  <DepositPaymentElement
                    currencySymbol={currencySymbol}
                    depositAmount={depositAmount}
                    fullName={`${customerFirstName} ${customerLastName}`.trim()}
                    customerEmail={customerEmail}
                    customerPhone={customerPhone}
                    setErrorMessage={setErrorMessage}
                    setSuccessMessage={setSuccessMessage}
                  />
                </Elements>
              ) : (
                <div style={{ fontSize: '13px', color: '#7a7060', fontFamily: 'sans-serif', textAlign: 'center', lineHeight: 1.7 }}>
                  Continue to load the secure Stripe payment form.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: summary + CTA */}
        <div style={{ background: '#080806', padding: 'clamp(24px, 6vw, 36px)', minWidth: 0, boxSizing: 'border-box' }}>
          <BookingSummary service={service} date={date} time={time} master={master} depositAmount={depositAmount} currencySymbol={currencySymbol} />

          {!clientSecret && (
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
                opacity: isStartPaymentDisabled ? 0.55 : 1,
                pointerEvents: isStartPaymentDisabled ? 'none' : 'auto',
              }}
              disabled={isStartPaymentDisabled}
              onClick={handleStartPayment}
              onMouseEnter={e => {
                if (isStartPaymentDisabled) return
                e.currentTarget.style.background = 'rgba(201,168,76,0.08)'
                e.currentTarget.style.boxShadow = '0 0 20px rgba(201,168,76,0.2)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              {isChecking ? 'Checking availability...' : 'Continue to secure payment →'}
            </button>
          )}

          {errorMessage && (
            <p style={{ fontSize: '12px', color: '#d06b5f', fontFamily: 'sans-serif', textAlign: 'center', marginTop: '14px', lineHeight: 1.6 }}>
              {errorMessage}
            </p>
          )}

          {successMessage && (
            <p style={{ fontSize: '12px', color: '#c9a84c', fontFamily: 'sans-serif', textAlign: 'center', marginTop: '14px', lineHeight: 1.6 }}>
              {successMessage}
            </p>
          )}

          <p style={{ fontSize: '11px', color: '#3a3020', fontFamily: 'sans-serif', textAlign: 'center', marginTop: '14px', lineHeight: 1.7 }}>
            Your {currencySymbol}{depositAmount} deposit confirms the booking. The remaining amount is paid at the salon.
          </p>
        </div>
      </div>
    </div>
  )
}

interface DepositPaymentElementProps {
  currencySymbol: string
  depositAmount: number
  fullName: string
  customerEmail: string
  customerPhone: string
  setErrorMessage: (message: string | null) => void
  setSuccessMessage: (message: string | null) => void
}

function DepositPaymentElement({
  currencySymbol,
  depositAmount,
  fullName,
  customerEmail,
  customerPhone,
  setErrorMessage,
  setSuccessMessage,
}: DepositPaymentElementProps) {
  const stripe = useStripe()
  const elements = useElements()
  const [isPaying, setIsPaying] = useState(false)
  const paymentElementOptions: StripePaymentElementOptions = {
    defaultValues: {
      billingDetails: {
        name: fullName,
        email: customerEmail,
        phone: customerPhone,
        address: {
          country: 'LT',
        },
      },
    },
  }

  const handlePayDeposit = async () => {
    setErrorMessage(null)
    setSuccessMessage(null)

    if (!stripe || !elements) {
      setErrorMessage('Could not start payment. Please try again.')
      return
    }

    setIsPaying(true)

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/booking/success`,
      },
    })

    if (error) {
      setErrorMessage(error.message ?? 'Could not start payment. Please try again.')
      setIsPaying(false)
    }
  }

  return (
    <div>
      <PaymentElement options={paymentElementOptions} />
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
          opacity: isPaying || !stripe || !elements ? 0.55 : 1,
          pointerEvents: isPaying || !stripe || !elements ? 'none' : 'auto',
        }}
        disabled={isPaying || !stripe || !elements}
        onClick={handlePayDeposit}
        onMouseEnter={e => {
          if (isPaying) return
          e.currentTarget.style.background = 'rgba(201,168,76,0.08)'
          e.currentTarget.style.boxShadow = '0 0 20px rgba(201,168,76,0.2)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.boxShadow = 'none'
        }}
      >
        {isPaying ? 'Processing payment...' : `Pay ${currencySymbol}${depositAmount} deposit →`}
      </button>
    </div>
  )
}
