import Stats from './Stats'
import { useHomeStats } from '../hooks/useHomeStats'

export default function HomeStatsSection() {
  const { data: stats = [] } = useHomeStats()

  return <Stats stats={stats} />
}