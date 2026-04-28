import { useEffect, useRef } from 'react'
import { useWorks } from '../hooks/useWorks'
import WorksPhoto from './WorksPhoto'
import { MOCK_MASTERS } from '../../../shared/data/mockData'

const masterMap = Object.fromEntries(MOCK_MASTERS.map(m => [m.id, m.name]))

export default function WorksGallery() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useWorks()

  const sentinelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const sentinel = sentinelRef.current
    if (!sentinel) return

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage()
        }
      },
      { rootMargin: '200px' },
    )

    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const allPhotos = data?.pages.flatMap(p => p.items) ?? []
  const total = data?.pages[0]?.total ?? 0

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
        <span style={{ color: '#c9a84c', fontFamily: 'sans-serif', fontSize: '11px', letterSpacing: '3px', textTransform: 'uppercase' }}>
          Loading...
        </span>
      </div>
    )
  }

  return (
    <div>
      <div style={{ columns: 3, columnGap: '8px' }}>
        {allPhotos.map(photo => (
          <WorksPhoto
            key={photo.id}
            photo={photo}
            masterName={masterMap[photo.master_id] ?? 'Master'}
          />
        ))}
      </div>

      <div ref={sentinelRef} style={{ height: '1px' }} />

      <div style={{ textAlign: 'center', padding: '40px 0 16px' }}>
        {isFetchingNextPage && (
          <span style={{ color: '#c9a84c', fontFamily: 'sans-serif', fontSize: '11px', letterSpacing: '3px', textTransform: 'uppercase' }}>
            Loading...
          </span>
        )}
        {!hasNextPage && allPhotos.length > 0 && !isFetchingNextPage && (
          <span style={{ color: '#7a7060', fontFamily: 'sans-serif', fontSize: '11px', letterSpacing: '2px' }}>
            All {total} works
          </span>
        )}
      </div>
    </div>
  )
}
