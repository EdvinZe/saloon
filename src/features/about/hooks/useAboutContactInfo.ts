import { useQuery } from '@tanstack/react-query'
import { getAboutContactInfo } from '../api'

export function useAboutContactInfo() {
  return useQuery({
    queryKey: ['about-contact-info'],
    queryFn: getAboutContactInfo,
    staleTime: 5 * 60_000,
  })
}