import { useEffect, useRef } from 'react'

export function useBookingStepScroll(step: number) {
  const step2Ref = useRef<HTMLDivElement>(null)
  const step3Ref = useRef<HTMLDivElement>(null)
  const step4Ref = useRef<HTMLDivElement>(null)

  const prevStep = useRef(step)

  useEffect(() => {
    if (step !== prevStep.current) {
      const refs: Record<number, React.RefObject<HTMLDivElement | null>> = {
        2: step2Ref,
        3: step3Ref,
        4: step4Ref,
      }

      const ref = refs[step]

      if (ref?.current) {
        setTimeout(() => {
          ref.current?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })
        }, 120)
      }
    }

    prevStep.current = step
  }, [step])

  return {
    step2Ref,
    step3Ref,
    step4Ref,
  }
}
