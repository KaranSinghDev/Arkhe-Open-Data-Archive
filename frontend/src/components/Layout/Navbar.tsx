import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function Navbar() {
  const { user, loading, login, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="text-lg font-bold text-brand-700 tracking-tight">
          Arkhe
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm">
          <Link to="/search" className="text-gray-600 hover:text-gray-900">Browse</Link>
          {user && (
            <>
              <Link to="/upload" className="text-gray-600 hover:text-gray-900">Upload</Link>
              <Link to="/my-records" className="text-gray-600 hover:text-gray-900">My Records</Link>
            </>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {loading ? (
            <div className="h-8 w-20 bg-gray-100 rounded animate-pulse" />
          ) : user ? (
            <div className="flex items-center gap-3 text-sm">
              <button
                onClick={() => navigate('/profile')}
                className="text-gray-700 hover:text-gray-900 font-medium"
              >
                {user.name}
              </button>
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              onClick={login}
              className="bg-brand-600 text-white text-sm px-4 py-1.5 rounded hover:bg-brand-700 transition-colors"
            >
              Sign in with ORCID
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
