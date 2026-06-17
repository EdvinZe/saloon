import type { ReactNode } from 'react'
import { useInView } from '../hooks/useInView'

interface Props {
  children: ReactNode
  id?: string
  minHeight?: string
}

export default function LoadableSection({
  children,
  id,
  minHeight = '300px',
}: Props) {
  const { ref, hasBeenVisible } = useInView<HTMLDivElement>()

  return (
    <div
      id={id}
      ref={ref}
      style={{
        minHeight: hasBeenVisible ? undefined : minHeight,
      }}
    >
      {hasBeenVisible && children}
    </div>
  )
}
