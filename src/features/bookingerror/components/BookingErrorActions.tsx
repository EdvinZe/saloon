import { Link, useNavigate } from 'react-router-dom'

interface Props {
  btn: string
  btnHref: string
  secondaryBtn?: string
  secondaryHref?: string
}

export default function BookingErrorActions({
  btn,
  btnHref,
  secondaryBtn,
  secondaryHref,
}: Props) {
  const navigate = useNavigate()

  return (
    <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
      <button
        onClick={() => navigate(btnHref)}
        style={{
          background: 'transparent',
          border: '1px solid #c9a84c',
          color: '#c9a84c',
          padding: '14px 28px',
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
        {btn}
      </button>

      {secondaryBtn && secondaryHref && (
        <Link to={secondaryHref} style={{ textDecoration: 'none' }}>
          <button
            style={{
              background: 'transparent',
              border: '1px solid #2a2218',
              color: '#7a7060',
              padding: '14px 28px',
              fontSize: '11px',
              letterSpacing: '3px',
              textTransform: 'uppercase',
              cursor: 'pointer',
              fontFamily: 'Georgia, serif',
              fontWeight: 400,
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = '#5a5040'
              e.currentTarget.style.color = '#e8e0d0'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = '#2a2218'
              e.currentTarget.style.color = '#7a7060'
            }}
          >
            {secondaryBtn}
          </button>
        </Link>
      )}
    </div>
  )
}
