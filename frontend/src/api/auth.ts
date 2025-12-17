import client from './client'

export interface User {
  id: string
  orcid_id: string
  name: string
  email: string | null
  created_at: string
}

export async function getLoginUrl(): Promise<{ url: string; state: string }> {
  const { data } = await client.get('/auth/login/orcid')
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await client.get('/auth/me')
  return data
}

export async function logout(): Promise<void> {
  await client.post('/auth/logout')
}
