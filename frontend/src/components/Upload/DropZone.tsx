import { DragEvent, useRef, useState } from 'react'

interface Props {
  onFiles: (files: File[]) => void
  accept?: string
}

export function DropZone({ onFiles, accept }: Props) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files)
    if (dropped.length) onFiles(dropped)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors ${
        dragging ? 'border-brand-500 bg-brand-50' : 'border-gray-300 hover:border-brand-400'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        multiple
        onChange={(e) => {
          const selected = Array.from(e.target.files ?? [])
          if (selected.length) onFiles(selected)
        }}
      />
      <p className="text-sm text-gray-500">
        Drop files here or <span className="text-brand-600 underline">browse</span>
      </p>
      <p className="text-xs text-gray-400 mt-1">CSV, JSON, PDF, ROOT, ZIP — max 2 GB</p>
    </div>
  )
}
