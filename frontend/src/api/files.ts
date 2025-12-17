import client from './client'

export interface FileRecord {
  id: string
  record_id: string
  filename: string
  content_type: string
  size_bytes: number | null
  parsed_metadata: Record<string, unknown> | null
  created_at: string
}

export interface FileList {
  items: FileRecord[]
  total: number
}

export async function listFiles(recordId: string): Promise<FileList> {
  const { data } = await client.get(`/records/${recordId}/files/`)
  return data
}

export async function uploadFile(
  recordId: string,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<FileRecord> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await client.post(`/records/${recordId}/files/`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  })
  return data
}

export function getDownloadUrl(recordId: string, fileId: string): string {
  return `/api/records/${recordId}/files/${fileId}/download`
}

export async function deleteFile(recordId: string, fileId: string): Promise<void> {
  await client.delete(`/records/${recordId}/files/${fileId}`)
}
