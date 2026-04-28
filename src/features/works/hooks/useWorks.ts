import { useInfiniteQuery } from '@tanstack/react-query'
import { getWorks } from '../api'

const PAGE_SIZE = 9

export function useWorks() {
  return useInfiniteQuery({
    queryKey: ['works'],
    queryFn: ({ pageParam }) => getWorks(pageParam, PAGE_SIZE),
    initialPageParam: 1,
    getNextPageParam: (lastPage, _allPages, lastPageParam) =>
      lastPage.has_more ? lastPageParam + 1 : undefined,
  })
}
