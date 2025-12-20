import type { Facets } from '../../api/search'

interface Filters {
  experiment?: string
  record_type?: string
  year?: number
}

interface Props {
  facets: Facets
  filters: Filters
  onChange: (filters: Filters) => void
}

export function FilterPanel({ facets, filters, onChange }: Props) {
  const set = (key: keyof Filters, value: string) => {
    const parsed = key === 'year' ? (value ? parseInt(value) : undefined) : value || undefined
    onChange({ ...filters, [key]: parsed })
  }

  return (
    <aside className="space-y-5 text-sm">
      <div>
        <h3 className="font-semibold text-gray-700 mb-2">Experiment</h3>
        <select
          value={filters.experiment ?? ''}
          onChange={(e) => set('experiment', e.target.value)}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        >
          <option value="">All experiments</option>
          {facets.experiments.map((b) => (
            <option key={b.key} value={b.key}>{b.key} ({b.count})</option>
          ))}
        </select>
      </div>

      <div>
        <h3 className="font-semibold text-gray-700 mb-2">Record type</h3>
        <select
          value={filters.record_type ?? ''}
          onChange={(e) => set('record_type', e.target.value)}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        >
          <option value="">All types</option>
          {facets.record_types.map((b) => (
            <option key={b.key} value={b.key}>{b.key} ({b.count})</option>
          ))}
        </select>
      </div>

      <div>
        <h3 className="font-semibold text-gray-700 mb-2">Year</h3>
        <select
          value={filters.year?.toString() ?? ''}
          onChange={(e) => set('year', e.target.value)}
          className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
        >
          <option value="">All years</option>
          {facets.years.map((b) => (
            <option key={b.key} value={b.key}>{b.key} ({b.count})</option>
          ))}
        </select>
      </div>

      {(filters.experiment || filters.record_type || filters.year) && (
        <button
          onClick={() => onChange({})}
          className="text-brand-600 hover:underline text-xs"
        >
          Clear filters
        </button>
      )}
    </aside>
  )
}
