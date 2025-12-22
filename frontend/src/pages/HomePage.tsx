import { useNavigate } from 'react-router-dom'
import { SearchBar } from '../components/Search/SearchBar'
import { useAuth } from '../hooks/useAuth'

export function HomePage() {
  const navigate = useNavigate()
  const { user, login } = useAuth()

  const handleSearch = (q: string) => {
    navigate(`/search${q ? `?q=${encodeURIComponent(q)}` : ''}`)
  }

  return (
    <div className="max-w-3xl mx-auto text-center py-16 space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Zenodo-Lite</h1>
        <p className="text-lg text-gray-600">
          Open scientific data repository for physics experiments.
          <br />Share datasets, software, and research outputs — FAIR and free.
        </p>
      </div>

      <SearchBar onSearch={handleSearch} />

      {!user && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left space-y-3">
          <h2 className="font-semibold text-blue-900">Share your research</h2>
          <p className="text-sm text-blue-700">
            Sign in with your free ORCID account to upload datasets, assign DOIs,
            and make your work findable by the global research community.
          </p>
          <button
            onClick={login}
            className="bg-brand-600 text-white text-sm px-5 py-2 rounded hover:bg-brand-700 transition-colors"
          >
            Sign in with ORCID — it's free
          </button>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 text-center text-sm">
        {[
          { label: 'Findable', desc: 'Full-text search with filters' },
          { label: 'Accessible', desc: 'Open downloads, pre-signed URLs' },
          { label: 'FAIR', desc: 'JSON-LD metadata on every record' },
        ].map((item) => (
          <div key={item.label} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="font-bold text-brand-700 mb-1">{item.label}</div>
            <div className="text-gray-500">{item.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
