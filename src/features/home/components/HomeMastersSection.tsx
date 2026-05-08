import MastersCarousel from './MastersCarousel'
import { useHomeMasters } from '../hooks/useHomeMasters'

export default function HomeMastersSection() {
  const { data: masters = [] } = useHomeMasters()

  return <MastersCarousel masters={masters} />
}