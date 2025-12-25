import { useAuth } from '../hooks/useAuth'
import { Link } from 'react-router-dom'

export function ProfilePage() {
  const { user, login, logout } = useAuth()

  if (!user) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <h1 className="text-xl font-bold text-gray-800">Sign in to view your profile</h1>
        <button onClick={login} className="bg-brand-600 text-white px-5 py-2 rounded hover:bg-brand-700 text-sm">
          Sign in with ORCID
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile</h1>

      <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
        <div className="p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-lg">
            {user.name?.charAt(0)?.toUpperCase() ?? '?'}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{user.name ?? 'Unknown'}</p>
            {user.email && <p className="text-sm text-gray-500">{user.email}</p>}
          </div>
        </div>

        <div className="p-5 space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">ORCID iD</span>
            <a
              href={`https://orcid.org/${user.orcid_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-600 hover:underline font-mono"
            >
              {user.orcid_id}
            </a>
          </div>
        </div>

        <div className="p-5 flex flex-col sm:flex-row gap-3">
          <Link
            to="/my-records"
            className="flex-1 text-center border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-50"
          >
            My records
          </Link>
          <Link
            to="/upload"
            className="flex-1 text-center bg-brand-600 text-white px-4 py-2 rounded text-sm hover:bg-brand-700"
          >
            Upload new record
          </Link>
        </div>
      </div>

      <button
        onClick={logout}
        className="mt-6 text-sm text-gray-400 hover:text-red-500 transition-colors"
      >
        Sign out
      </button>
    </div>
  )
}
