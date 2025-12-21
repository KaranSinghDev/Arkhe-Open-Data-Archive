import { useEffect, useState } from 'react'
import { listFiles, getDownloadUrl, type FileRecord } from '../../api/files'

function formatBytes(n: number | null): string {
  if (!n) return '—'
  if (n < 1024) return `${n} B`
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`
  return `${(n / 1024 ** 3).toFixed(2)} GB`
}

export function FileList({ recordId }: { recordId: string }) {
  const [files, setFiles] = useState<FileRecord[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listFiles(recordId)
      .then((r) => setFiles(r.items))
      .catch(() => setFiles([]))
      .finally(() => setLoading(false))
  }, [recordId])

  if (loading) return <div className="h-8 bg-gray-100 rounded animate-pulse" />
  if (!files.length) return <p className="text-sm text-gray-500">No files attached.</p>

  return (
    <ul className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden text-sm">
      {files.map((f) => (
        <li key={f.id} className="flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50">
          <div>
            <span className="font-medium text-gray-800">{f.filename}</span>
            <span className="ml-2 text-gray-400">{formatBytes(f.size_bytes)}</span>
          </div>
          <a
            href={getDownloadUrl(recordId, f.id)}
            className="text-brand-600 hover:underline ml-4"
            download={f.filename}
          >
            Download
          </a>
        </li>
      ))}
    </ul>
  )
}
