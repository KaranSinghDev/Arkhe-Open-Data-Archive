import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getRecord, type Record } from '../api/records'
import { FileList } from '../components/Records/FileList'
import { FAIRBadge } from '../components/Records/FAIRBadge'

export function RecordPage() {
  const { id } = useParams<{ id: string }>()
  const [record, setRecord] = useState<Record | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!id) return
    getRecord(id)
      .then(setRecord)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="animate-pulse space-y-4"><div className="h-8 bg-gray-200 rounded w-2/3" /><div className="h-4 bg-gray-100 rounded w-full" /></div>
  if (error || !record) return <div className="text-center py-16 text-gray-500">Record not found. <Link to="/search" className="text-brand-600 underline">Browse all records</Link></div>

  return (
    <div className="max-w-3xl">
      <div className="flex items-start gap-3 mb-2">
        <h1 className="text-2xl font-bold text-gray-900 flex-1">{record.title}</h1>
        <FAIRBadge />
      </div>

      <div className="flex flex-wrap gap-2 text-xs mb-4">
        <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded">{record.record_type}</span>
        {record.experiment && <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded">{record.experiment}</span>}
        {record.year && <span className="text-gray-500">{record.year}</span>}
        <span className="text-gray-400">License: {record.license}</span>
      </div>

      {record.doi && (
        <p className="text-sm text-gray-500 mb-4">DOI: <code className="bg-gray-100 px-1 rounded">{record.doi}</code></p>
      )}

      {record.description && (
        <p className="text-gray-700 mb-6 whitespace-pre-wrap">{record.description}</p>
      )}

      {record.keywords?.length ? (
        <div className="flex flex-wrap gap-1.5 mb-6">
          {record.keywords.map((kw) => (
            <Link key={kw} to={`/search?q=${encodeURIComponent(kw)}`}
              className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded hover:bg-green-100">
              #{kw}
            </Link>
          ))}
        </div>
      ) : null}

      <h2 className="text-base font-semibold text-gray-800 mb-3">Files</h2>
      <FileList recordId={record.id} />

      <div className="mt-6 text-xs text-gray-400">
        <a href={`/api/records/${record.id}/metadata.json`} target="_blank" rel="noopener noreferrer"
          className="text-brand-500 hover:underline">
          View JSON-LD metadata
        </a>
      </div>
    </div>
  )
}
