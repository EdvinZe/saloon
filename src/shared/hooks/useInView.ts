import { useEffect, useRef, useState } from 'react'

interface Options {
  rootMargin?: string
  threshold?: number
}

export function useInView<T extends HTMLElement>({
  rootMargin = '200px',
  threshold = 0,
}: Options = {}) {
  const ref = useRef<T | null>(null)
  const [hasBeenVisible, setHasBeenVisible] = useState(false)

  useEffect(() => {
    const element = ref.current

    if (!element || hasBeenVisible) return

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) {
          setHasBeenVisible(true)
          observer.disconnect()
        }
      },
      {
        rootMargin,
        threshold,
      },
    )

    observer.observe(element)

    return () => observer.disconnect()
  }, [rootMargin, threshold, hasBeenVisible])

  return {
    ref,
    hasBeenVisible,
  }
}