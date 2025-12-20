import { Link } from 'react-router-dom'
import type { SearchHit } from '../../api/search'

export function RecordCard({ hit }: { hit: SearchHit }) {
  return (
    <article className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <Link
            to={`/records/${hit.id}`}
            className="text-base font-semibold text-brand-700 hover:underline line-clamp-2"
          >
            {hit.title}
          </Link>
          {hit.description && (
            <p className="mt-1.5 text-sm text-gray-600 line-clamp-2">{hit.description}</p>
          )}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded">{hit.record_type}</span>
        {hit.experiment && (
          <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded">{hit.experiment}</span>
        )}
        {hit.year && (
          <span className="bg-gray-50 text-gray-600 px-2 py-0.5 rounded">{hit.year}</span>
        )}
        {hit.keywords?.slice(0, 3).map((kw) => (
          <span key={kw} className="bg-green-50 text-green-700 px-2 py-0.5 rounded">#{kw}</span>
        ))}
      </div>
    </article>
  )
}
