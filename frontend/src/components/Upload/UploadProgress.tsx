interface Props {
  filename: string
  progress: number
  error?: string
}

export function UploadProgress({ filename, progress, error }: Props) {
  return (
    <div className="text-sm">
      <div className="flex justify-between mb-1">
        <span className="truncate text-gray-700">{filename}</span>
        <span className="ml-4 text-gray-500">{error ? 'Failed' : `${progress}%`}</span>
      </div>
      <div className="h-1.5 rounded-full bg-gray-200">
        <div
          className={`h-1.5 rounded-full transition-all ${error ? 'bg-red-400' : 'bg-brand-500'}`}
          style={{ width: `${progress}%` }}
        />
      </div>
      {error && <p className="mt-1 text-red-500 text-xs">{error}</p>}
    </div>
  )
}
