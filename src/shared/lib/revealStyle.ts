import type { CSSProperties } from 'react'

export function revealStyle(visible: boolean): CSSProperties {
  return {
    maxHeight: visible ? '2000px' : '0',
    opacity: visible ? 1 : 0,
    overflow: 'hidden',
    transition: 'max-height 0.6s ease, opacity 0.5s ease',
    scrollMarginTop: '24px',
  }
}
