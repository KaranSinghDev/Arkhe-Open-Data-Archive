import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { createRecord, updateRecord } from '../api/records'
import { uploadFile } from '../api/files'
import { DropZone } from '../components/Upload/DropZone'
import { UploadProgress } from '../components/Upload/UploadProgress'

interface UploadState {
  file: File
  progress: number
  error?: string
}

export function UploadPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [recordType, setRecordType] = useState('dataset')
  const [experiment, setExperiment] = useState('')
  const [year, setYear] = useState('')
  const [license, setLicense] = useState('CC-BY-4.0')
  const [keywords, setKeywords] = useState('')
  const [uploads, setUploads] = useState<UploadState[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!user) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <h1 className="text-xl font-bold text-gray-800">Sign in to upload</h1>
        <p className="text-gray-500 text-sm">You need a free ORCID account to share research data.</p>
        <button onClick={login} className="bg-brand-600 text-white px-5 py-2 rounded hover:bg-brand-700 text-sm">
          Sign in with ORCID
        </button>
      </div>
    )
  }

  const handleFiles = (files: File[]) => {
    setUploads(files.map((file) => ({ file, progress: 0 })))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) { setError('Title is required'); return }
    setSubmitting(true)
    setError('')
    try {
      const record = await createRecord({
        title: title.trim(),
        description: description.trim() || undefined,
        record_type: recordType,
        experiment: experiment.trim() || undefined,
        year: year ? parseInt(year) : undefined,
        license,
        keywords: keywords ? keywords.split(',').map((k) => k.trim()).filter(Boolean) : undefined,
      })

      for (let i = 0; i < uploads.length; i++) {
        try {
          await uploadFile(record.id, uploads[i].file, (pct) => {
            setUploads((prev) => prev.map((u, idx) => idx === i ? { ...u, progress: pct } : u))
          })
        } catch {
          setUploads((prev) => prev.map((u, idx) => idx === i ? { ...u, error: 'Upload failed' } : u))
        }
      }

      await updateRecord(record.id, { status: 'published' })
      navigate(`/records/${record.id}`)
    } catch {
      setError('Failed to create record. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload research data</h1>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)}
            rows={4} className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Record type</label>
            <select value={recordType} onChange={(e) => setRecordType(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              {['dataset', 'software', 'paper', 'simulation', 'other'].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Experiment</label>
            <input value={experiment} onChange={(e) => setExperiment(e.target.value)} placeholder="CMS, ATLAS, LHCb…"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
            <input type="number" value={year} onChange={(e) => setYear(e.target.value)} placeholder={String(new Date().getFullYear())}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">License</label>
            <select value={license} onChange={(e) => setLicense(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              {['CC-BY-4.0', 'CC0-1.0', 'MIT'].map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Keywords (comma-separated)</label>
          <input value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="proton, collision, run3"
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Files</label>
          <DropZone onFiles={handleFiles} />
          {uploads.length > 0 && (
            <div className="mt-3 space-y-2">
              {uploads.map((u, i) => (
                <UploadProgress key={i} filename={u.file.name} progress={u.progress} error={u.error} />
              ))}
            </div>
          )}
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button type="submit" disabled={submitting}
          className="w-full bg-brand-600 text-white py-2.5 rounded font-medium text-sm hover:bg-brand-700 disabled:opacity-60 transition-colors">
          {submitting ? 'Uploading…' : 'Publish record'}
        </button>
      </form>
    </div>
  )
}
