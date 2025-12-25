import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="max-w-md mx-auto text-center py-24 space-y-4">
      <p className="text-6xl font-bold text-gray-200">404</p>
      <h1 className="text-xl font-semibold text-gray-800">Page not found</h1>
      <p className="text-gray-500 text-sm">The page you're looking for doesn't exist or has been moved.</p>
      <div className="flex justify-center gap-4 pt-2">
        <Link to="/" className="bg-brand-600 text-white px-5 py-2 rounded text-sm hover:bg-brand-700">
          Go home
        </Link>
        <Link to="/search" className="border border-gray-300 text-gray-700 px-5 py-2 rounded text-sm hover:bg-gray-50">
          Browse records
        </Link>
      </div>
    </div>
  )
}
