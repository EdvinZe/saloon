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
  const view = useInView<HTMLDivElement>()

  return (
    <div
      id={id}
      ref={view.ref}
      style={{
        minHeight: view.hasBeenVisible ? undefined : minHeight,
      }}
    >
      {view.hasBeenVisible && children}
    </div>
  )
}