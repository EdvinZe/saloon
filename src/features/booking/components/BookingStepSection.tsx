import { forwardRef, type ReactNode } from 'react'
import { revealStyle } from '../../../shared/lib/revealStyle'

type BookingStepSectionProps = {
  visible: boolean
  children: ReactNode
}

const BookingStepSection = forwardRef<HTMLDivElement, BookingStepSectionProps>(
  ({ visible, children }, ref) => (
    <div ref={ref} style={revealStyle(visible)}>
      {children}
    </div>
  ),
)

export default BookingStepSection
