import type { CSSProperties } from 'react'

interface BookingManageDetailsRow {
  label: string
  value: string
  gold?: boolean
}

interface Props {
  rows: BookingManageDetailsRow[]
}

const ROW: CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'baseline',
  padding: '10px 0',
}

export default function BookingManageDetailsCard({ rows }: Props) {
  return (
    <div style={{ background: '#141008', border: '1px solid #2a2218', padding: '24px 28px', marginBottom: '20px' }}>
      {rows.map((row, i) => (
        <div key={row.label} style={{ ...ROW, borderBottom: i < rows.length - 1 ? '1px solid #1a1810' : 'none' }}>
          <span style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '1px' }}>
            {row.label}
          </span>
          <span style={{ fontSize: '13px', color: row.gold ? '#c9a84c' : '#e8e0d0', fontFamily: 'sans-serif' }}>
            {row.value}
          </span>
        </div>
      ))}
    </div>
  )
}
