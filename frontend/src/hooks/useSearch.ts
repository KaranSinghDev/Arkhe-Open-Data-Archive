import { useState, useCallback } from 'react'
import { search, type SearchParams, type SearchResponse } from '../api/search'

interface UseSearchResult {
  data: SearchResponse | null
  loading: boolean
  error: string | null
  run: (params: SearchParams) => Promise<void>
}

export function useSearch(): UseSearchResult {
  const [data, setData] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = useCallback(async (params: SearchParams) => {
    setLoading(true)
    setError(null)
    try {
      const result = await search(params)
      setData(result)
    } catch {
      setError('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, run }
}
