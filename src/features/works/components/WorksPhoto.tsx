import { useState } from 'react'
import type { WorkPhoto } from '../../../shared/data/mockData'

interface Props {
  photo: WorkPhoto
  masterName: string
}

export default function WorksPhoto({ photo, masterName }: Props) {
  const [hovered, setHovered] = useState(false)
  const aspectRatio = photo.aspect_ratio === '1:1' ? '1 / 1' : '3 / 4'

  return (
    <div
      style={{
        breakInside: 'avoid',
        marginBottom: '8px',
        position: 'relative',
        overflow: 'hidden',
        cursor: 'pointer',
        background: '#141008',
        border: '1px solid #2a2218',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {photo.photo_url ? (
        <img
          src={photo.photo_url}
          alt={`Work by ${masterName}`}
          style={{ display: 'block', width: '100%', aspectRatio, objectFit: 'cover' }}
        />
      ) : (
        <div style={{
          width: '100%',
          aspectRatio,
          background: 'linear-gradient(135deg, #141008 0%, #1c1610 60%, #0f0f0f 100%)',
        }} />
      )}

      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'rgba(0,0,0,0.4)',
        display: 'flex',
        alignItems: 'flex-end',
        padding: '14px',
        opacity: hovered ? 1 : 0,
        transition: 'opacity 0.25s',
        pointerEvents: 'none',
      }}>
        <span style={{
          color: '#c9a84c',
          fontSize: '11px',
          letterSpacing: '2px',
          textTransform: 'uppercase',
          fontFamily: 'sans-serif',
        }}>
          {masterName}
        </span>
      </div>
    </div>
  )
}
