import client from './client'

export interface Record {
  id: string
  user_id: string
  title: string
  description: string | null
  doi: string | null
  record_type: string
  experiment: string | null
  year: number | null
  license: string
  keywords: string[] | null
  status: string
  created_at: string
  updated_at: string
}

export interface RecordList {
  items: Record[]
  total: number
  page: number
  size: number
}

export interface RecordCreate {
  title: string
  description?: string
  doi?: string
  record_type: string
  experiment?: string
  year?: number
  license?: string
  keywords?: string[]
}

export interface RecordUpdate extends Partial<RecordCreate> {
  status?: string
}

export async function listRecords(page = 1, size = 20): Promise<RecordList> {
  const { data } = await client.get('/records/', { params: { page, size } })
  return data
}

export async function getRecord(id: string): Promise<Record> {
  const { data } = await client.get(`/records/${id}`)
  return data
}

export async function createRecord(payload: RecordCreate): Promise<Record> {
  const { data } = await client.post('/records/', payload)
  return data
}

export async function updateRecord(id: string, payload: RecordUpdate): Promise<Record> {
  const { data } = await client.patch(`/records/${id}`, payload)
  return data
}

export async function deleteRecord(id: string): Promise<void> {
  await client.delete(`/records/${id}`)
}

export async function getFairMetadata(id: string): Promise<object> {
  const { data } = await client.get(`/records/${id}/metadata.json`)
  return data
}
