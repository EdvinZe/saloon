import { useEffect, useState } from 'react'
import type { Master } from '../../masters/api'
import type { Service } from '../../services/api'
import { useManageAvailableMasters } from '../hooks/useManageAvailableMasters'

interface Props {
  service: Service
  date: string
  time: string
  selected: Master | null
  onSelect: (m: Master | null) => void
  disabled?: boolean
}

export default function ManageMasterSelect({ service, date, time, selected, onSelect, disabled = false }: Props) {
  const { data: masters = [], isLoading } = useManageAvailableMasters(date, time, service.id)
  const [showChooseAvailableMessage, setShowChooseAvailableMessage] = useState(false)

  useEffect(() => {
    setShowChooseAvailableMessage(false)
  }, [date, time])

  useEffect(() => {
    if (isLoading || !selected) return

    const selectedIsAvailable = masters.some(master => master.id === selected.id)
    if (!selectedIsAvailable) {
      setShowChooseAvailableMessage(true)
      onSelect(null)
    }
  }, [isLoading, masters, selected, onSelect])

  const handleSelect = (master: Master) => {
    setShowChooseAvailableMessage(false)
    onSelect(master)
  }

  return (
    <div style={{ width: '100%', minWidth: 0 }}>
      <p style={{
        fontSize: '10px', letterSpacing: '3px', color: '#c9a84c',
        textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '14px',
      }}>
        Step 3 — Barber
      </p>

      {isLoading ? (
        <div style={{ fontSize: '11px', color: '#5a5040', fontFamily: 'sans-serif', letterSpacing: '2px', padding: '8px 0' }}>
          Loading available barbers...
        </div>
      ) : masters.length === 0 ? (
        <div style={{ fontSize: '12px', color: '#5a5040', fontFamily: 'sans-serif', lineHeight: 1.6 }}>
          No barbers available at this time. Please choose another time.
        </div>
      ) : (
        <>
          {showChooseAvailableMessage && (
            <div style={{ fontSize: '12px', color: '#8a6040', fontFamily: 'sans-serif', lineHeight: 1.6, marginBottom: '12px' }}>
              Please choose an available barber.
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1px', background: '#2a2218', width: '100%', boxSizing: 'border-box', minWidth: 0 }}>
            {masters.map(master => {
              const sel = selected?.id === master.id
              return (
                <div
                  key={master.id}
                  onClick={() => { if (!disabled) handleSelect(master) }}
                  style={{
                    background: sel ? 'rgba(201,168,76,0.06)' : '#141008',
                    padding: '20px 16px',
                    textAlign: 'center',
                    cursor: disabled ? 'not-allowed' : 'pointer',
                    outline: sel ? '1px solid #c9a84c' : '1px solid transparent',
                    outlineOffset: '-1px',
                    opacity: disabled ? 0.5 : 1,
                    transition: 'all 0.2s',
                    boxSizing: 'border-box',
                    minWidth: 0,
                    overflow: 'hidden',
                  }}
                  onMouseEnter={e => { if (!disabled && !sel) (e.currentTarget as HTMLDivElement).style.background = 'rgba(201,168,76,0.03)' }}
                  onMouseLeave={e => { if (!sel) (e.currentTarget as HTMLDivElement).style.background = '#141008' }}
                >
                  <div style={{
                    width: '48px', height: '48px', borderRadius: '50%',
                    border: `1px solid ${sel ? '#c9a84c' : '#3a3020'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '16px', color: '#c9a84c', fontFamily: 'sans-serif',
                    margin: '0 auto 12px', transition: 'border-color 0.2s',
                  }}>
                    {master.initials}
                  </div>
                  <div style={{ fontSize: '15px', color: '#e8e0d0', marginBottom: '4px' }}>{master.name}</div>
                  <div style={{ fontSize: '10px', color: '#c9a84c', letterSpacing: '2px', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '10px' }}>
                    {master.role}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', maxWidth: '100%', minWidth: 0, marginTop: '12px' }}>
                    {master.services.map(service => (
                      <span
                        key={service.id}
                        style={{
                          fontSize: '10px',
                          lineHeight: 1,
                          color: '#7a7060',
                          fontFamily: 'sans-serif',
                          border: '1px solid rgba(214, 168, 79, 0.16)',
                          background: 'rgba(255,255,255,0.025)',
                          padding: '4px 8px',
                          whiteSpace: 'nowrap',
                          maxWidth: '100%',
                          boxSizing: 'border-box',
                        }}
                      >
                        {service.name}
                      </span>
                    ))}
                  </div>
                  {sel && (
                    <div style={{ marginTop: '10px', fontSize: '9px', letterSpacing: '2px', textTransform: 'uppercase', color: '#c9a84c', fontFamily: 'sans-serif' }}>
                      ✓ Selected
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
