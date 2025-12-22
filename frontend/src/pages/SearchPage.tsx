import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { SearchBar } from '../components/Search/SearchBar'
import { FilterPanel } from '../components/Search/FilterPanel'
import { RecordCard } from '../components/Records/RecordCard'
import { SkeletonList } from '../components/LoadingSkeleton'
import { useSearch } from '../hooks/useSearch'
import { usePagination } from '../hooks/usePagination'
import type { Facets } from '../api/search'

const EMPTY_FACETS: Facets = { experiments: [], record_types: [], years: [] }

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { data, loading, run } = useSearch()
  const { page, size, goTo, reset } = usePagination()
  const [filters, setFilters] = useState({
    experiment: searchParams.get('experiment') ?? undefined,
    record_type: searchParams.get('record_type') ?? undefined,
    year: searchParams.get('year') ? parseInt(searchParams.get('year')!) : undefined,
  })

  const q = searchParams.get('q') ?? ''

  useEffect(() => {
    run({ q, ...filters, page, size })
  }, [q, filters, page, size])

  const handleSearch = (newQ: string) => {
    setSearchParams({ q: newQ })
    reset()
  }

  const handleFilters = (newFilters: typeof filters) => {
    setFilters(newFilters)
    reset()
  }

  const facets = data?.facets ?? EMPTY_FACETS

  return (
    <div>
      <div className="mb-6">
        <SearchBar initialValue={q} onSearch={handleSearch} />
      </div>

      <div className="flex gap-8">
        <div className="w-52 shrink-0 hidden md:block">
          <FilterPanel facets={facets} filters={filters} onChange={handleFilters} />
        </div>

        <div className="flex-1 min-w-0">
          {loading ? (
            <SkeletonList />
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-4">
                {data ? `${data.total.toLocaleString()} results` : ''}
                {q && <span> for <strong>"{q}"</strong></span>}
              </p>
              {data?.hits.length === 0 && (
                <p className="text-gray-500 text-sm">No records found. Try a different search.</p>
              )}
              <div className="space-y-4">
                {data?.hits.map((hit) => <RecordCard key={hit.id} hit={hit} />)}
              </div>
              {data && data.total > size && (
                <div className="flex justify-center gap-3 mt-8 text-sm">
                  <button disabled={page === 1} onClick={() => goTo(page - 1)}
                    className="px-3 py-1.5 border rounded disabled:opacity-40">Prev</button>
                  <span className="px-3 py-1.5 text-gray-600">Page {page}</span>
                  <button disabled={page * size >= data.total} onClick={() => goTo(page + 1)}
                    className="px-3 py-1.5 border rounded disabled:opacity-40">Next</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
