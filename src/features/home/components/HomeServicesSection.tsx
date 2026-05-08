import Services from './Services'
import { useHomeServices } from '../hooks/useHomeServices'

export default function HomeServicesSection() {
  const { data: services = [] } = useHomeServices()

  return <Services services={services} />
}