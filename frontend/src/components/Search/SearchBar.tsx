import { type FormEvent, useState } from 'react'

interface Props {
  initialValue?: string
  onSearch: (q: string) => void
  placeholder?: string
}

export function SearchBar({ initialValue = '', onSearch, placeholder = 'Search datasets, software, papers…' }: Props) {
  const [value, setValue] = useState(initialValue)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSearch(value.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      <button
        type="submit"
        className="bg-brand-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
      >
        Search
      </button>
    </form>
  )
}
