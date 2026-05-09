import { format } from 'date-fns'
import type { Service, Master } from '../../../shared/data/mockData'

interface Props {
  service: Service | null
  date: string | null
  time: string | null
  master: Master | null
  depositAmount: number
  currencySymbol: string
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  padding: '10px 0',
  borderBottom: '1px solid #1a1810',
}

export default function BookingSummary({ service, date, time, master, depositAmount, currencySymbol }: Props) {
  const formattedDate = date
    ? format(new Date(date + 'T12:00:00'), 'EEEE, MMM d')
    : '—'

  const rows = [
    { label: 'Service',  value: service?.name ?? '—' },
    { label: 'Date',     value: formattedDate },
    { label: 'Time',     value: time ?? '—' },
    { label: 'Barber',   value: master?.name ?? '—' },
    { label: 'Duration', value: service?.dur ?? '—' },
  ]

  return (
    <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px' }}>
      <div style={{ fontSize: '10px', letterSpacing: '4px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '16px' }}>
        Booking summary
      </div>

      {rows.map(row => (
        <div key={row.label} style={rowStyle}>
          <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>{row.label}</span>
          <span style={{ fontSize: '13px', color: '#e8e0d0', fontFamily: 'sans-serif' }}>{row.value}</span>
        </div>
      ))}

      <div style={{ ...rowStyle, borderBottom: 'none', paddingTop: '14px' }}>
        <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif' }}>Total</span>
        <span style={{ fontSize: '16px', color: '#c9a84c', fontFamily: 'Georgia, serif' }}>{service?.price ?? '—'}</span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingTop: '6px' }}>
        <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif' }}>Deposit due today</span>
        <span style={{ fontSize: '20px', color: '#c9a84c', fontFamily: 'Georgia, serif' }}>
          {service ? `${currencySymbol}${depositAmount}` : '—'}
        </span>
      </div>
    </div>
  )
}
