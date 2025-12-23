import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { listRecords, deleteRecord, type Record } from '../api/records'

export function MyRecordsPage() {
  const { user, login } = useAuth()
  const [records, setRecords] = useState<Record[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    if (!user) return
    listRecords(1, 50)
      .then(({ items, total }) => { setRecords(items); setTotal(total) })
      .catch(() => setError('Failed to load records.'))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <h1 className="text-xl font-bold text-gray-800">Sign in to view your records</h1>
        <button onClick={login} className="bg-brand-600 text-white px-5 py-2 rounded hover:bg-brand-700 text-sm">
          Sign in with ORCID
        </button>
      </div>
    )
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this record permanently?')) return
    setDeleting(id)
    try {
      await deleteRecord(id)
      setRecords((prev) => prev.filter((r) => r.id !== id))
      setTotal((t) => t - 1)
    } catch {
      setError('Failed to delete record.')
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My records</h1>
        <Link to="/upload" className="bg-brand-600 text-white px-4 py-2 rounded text-sm hover:bg-brand-700">
          + New record
        </Link>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      ) : records.length === 0 ? (
        <div className="text-center py-16 text-gray-500 space-y-3">
          <p>You haven't uploaded any records yet.</p>
          <Link to="/upload" className="text-brand-600 hover:underline text-sm">Upload your first dataset</Link>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">{total} record{total !== 1 ? 's' : ''}</p>
          <div className="space-y-3">
            {records.map((record) => (
              <div key={record.id} className="bg-white border border-gray-200 rounded-lg p-4 flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <Link to={`/records/${record.id}`} className="font-medium text-gray-900 hover:text-brand-600 text-sm truncate block">
                    {record.title}
                  </Link>
                  <div className="flex flex-wrap gap-2 mt-1 text-xs text-gray-500">
                    <span className="bg-gray-100 px-1.5 py-0.5 rounded">{record.record_type}</span>
                    {record.experiment && <span>{record.experiment}</span>}
                    {record.year && <span>{record.year}</span>}
                    <span className={record.status === 'published' ? 'text-green-600' : 'text-yellow-600'}>
                      {record.status}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Link to={`/records/${record.id}`}
                    className="text-xs text-brand-600 border border-brand-200 px-2 py-1 rounded hover:bg-brand-50">
                    View
                  </Link>
                  <button
                    onClick={() => handleDelete(record.id)}
                    disabled={deleting === record.id}
                    className="text-xs text-red-500 border border-red-200 px-2 py-1 rounded hover:bg-red-50 disabled:opacity-50">
                    {deleting === record.id ? '…' : 'Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
