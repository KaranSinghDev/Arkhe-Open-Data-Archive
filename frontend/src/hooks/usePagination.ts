import { useState } from 'react'

export function usePagination(initialSize = 20) {
  const [page, setPage] = useState(1)
  const size = initialSize

  const next = () => setPage((p) => p + 1)
  const prev = () => setPage((p) => Math.max(1, p - 1))
  const goTo = (n: number) => setPage(Math.max(1, n))
  const reset = () => setPage(1)

  return { page, size, next, prev, goTo, reset }
}
