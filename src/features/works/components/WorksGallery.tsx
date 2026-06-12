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
          Loading works...
        </span>
      </div>
    )
  }

  return (
    <div>
      <style>
        {`
          .works-gallery-grid { columns: 3; column-gap: 8px; }
          @media (max-width: 899px) { .works-gallery-grid { columns: 2; } }
          @media (max-width: 520px) { .works-gallery-grid { columns: 1; } }
        `}
      </style>

      {allPhotos.length === 0 ? (
        <div style={{ border: '1px solid #2a2218', background: '#141008', padding: '28px 24px', textAlign: 'center', color: '#7a7060', fontFamily: 'sans-serif', fontSize: '13px', lineHeight: 1.7 }}>
          No work photos are available right now. Please check back soon.
        </div>
      ) : (
        <div className="works-gallery-grid">
          {allPhotos.map(photo => (
            <WorksPhoto
              key={photo.id}
              photo={photo}
              masterName={masterMap[photo.master_id] ?? 'Master'}
            />
          ))}
        </div>
      )}

      <div ref={sentinelRef} style={{ height: '1px' }} />

      <div style={{ textAlign: 'center', padding: '40px 0 16px' }}>
        {isFetchingNextPage && (
          <span style={{ color: '#c9a84c', fontFamily: 'sans-serif', fontSize: '11px', letterSpacing: '3px', textTransform: 'uppercase' }}>
            Loading more works...
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
