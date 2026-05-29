import type { ErrorConfig } from '../config/bookingErrorConfig'
import BookingErrorIcon from './BookingErrorIcon'
import BookingErrorActions from './BookingErrorActions'

interface Props {
  config: ErrorConfig
}

export default function BookingErrorContent({ config }: Props) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '80px 24px',
      minHeight: 'calc(100vh - 70px)',
    }}>
      <div style={{ width: '100%', maxWidth: '480px', textAlign: 'center' }}>
        {/* Dark-red X circle */}
        <BookingErrorIcon />

        <h1 style={{ fontSize: '32px', color: '#e8e0d0', fontWeight: 400, fontFamily: 'Georgia, serif', marginBottom: '16px' }}>
          {config.title}
        </h1>
        <p style={{ fontSize: '14px', color: '#7a7060', fontFamily: 'sans-serif', lineHeight: 1.8, maxWidth: '400px', margin: '0 auto 40px' }}>
          {config.sub}
        </p>

        <BookingErrorActions
          btn={config.btn}
          btnHref={config.btnHref}
          secondaryBtn={config.secondaryBtn}
          secondaryHref={config.secondaryHref}
        />
      </div>
    </div>
  )
}
