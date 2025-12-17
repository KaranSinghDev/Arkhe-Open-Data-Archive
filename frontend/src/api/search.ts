import client from './client'

export interface SearchHit {
  id: string
  title: string
  description: string | null
  experiment: string | null
  record_type: string
  year: number | null
  keywords: string[] | null
  score: number
}

export interface FacetBucket {
  key: string
  count: number
}

export interface Facets {
  experiments: FacetBucket[]
  record_types: FacetBucket[]
  years: FacetBucket[]
}

export interface SearchResponse {
  hits: SearchHit[]
  total: number
  page: number
  size: number
  facets: Facets
}

export interface SearchParams {
  q?: string
  experiment?: string
  record_type?: string
  year?: number
  keywords?: string[]
  page?: number
  size?: number
}

export async function search(params: SearchParams): Promise<SearchResponse> {
  const { data } = await client.get('/search/', { params })
  return data
}

export async function getFacets(): Promise<Facets> {
  const { data } = await client.get('/search/facets')
  return data
}

export async function suggest(q: string): Promise<string[]> {
  const { data } = await client.get('/search/suggest', { params: { q } })
  return data
}
