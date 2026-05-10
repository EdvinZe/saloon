import { Fragment } from 'react'

interface Props {
  step: number
}

const STEPS = ['Service', 'Date & Time', 'Barber', 'Payment']

export default function BookingProgress({ step }: Props) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      maxWidth: '560px',
      margin: '0 auto 52px',
      width: '100%',
      minWidth: 0,
      boxSizing: 'border-box',
    }}>
      {STEPS.map((label, i) => {
        const num = i + 1
        const done = step > num
        const active = step === num

        return (
          <Fragment key={label}>
            {i > 0 && (
              <div style={{
                flex: 1,
                height: '1px',
                background: step > i ? '#c9a84c' : '#2a2218',
                marginTop: '17px',
                transition: 'background 0.4s ease',
              }} />
            )}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', minWidth: 0 }}>
              <div style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                border: `1px solid ${done || active ? '#c9a84c' : '#2a2218'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: done ? '15px' : '13px',
                color: done || active ? '#c9a84c' : '#3a3020',
                background: done ? 'rgba(201,168,76,0.1)' : 'transparent',
                fontFamily: 'Georgia, serif',
                transition: 'all 0.3s ease',
              }}>
                {done ? '✓' : num}
              </div>
              <span style={{
                fontSize: '9px',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                color: active ? '#c9a84c' : done ? '#7a7060' : '#3a3020',
                fontFamily: 'sans-serif',
                whiteSpace: 'nowrap',
                transition: 'color 0.3s ease',
                textAlign: 'center',
              }}>
                {label}
              </span>
            </div>
          </Fragment>
        )
      })}
    </div>
  )
}
