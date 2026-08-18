import axios from 'axios'
import type { Evidence, ProvenanceEvent, Report } from '../types'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  return config
})

export async function analyzeMedia(file: File): Promise<Evidence> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<Evidence>('/analyze', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  return data
}

export async function verifyEvidence(evidenceId?: string, file?: File): Promise<any> {
  if (file) {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post('/verify', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    return data
  }
  if (evidenceId) {
    const form = new FormData()
    const { data } = await api.post('/verify', form, { params: { evidence_id: evidenceId } })
    return data
  }
  return {}
}

export async function listEvidence(): Promise<Evidence[]> {
  const { data } = await api.get<Evidence[]>('/evidence')
  return data
}

export async function getEvidence(evidenceId: string): Promise<Evidence> {
  const { data } = await api.get<Evidence>(`/evidence/${evidenceId}`)
  return data
}

export async function getProvenance(evidenceId: string): Promise<ProvenanceEvent[]> {
  const { data } = await api.get<ProvenanceEvent[]>(`/provenance/${evidenceId}`)
  return data
}

export async function getBlockchainRecord(evidenceId: string): Promise<any> {
  const { data } = await api.get(`/blockchain/${evidenceId}`)
  return data
}

export async function generateReport(evidenceId: string): Promise<Report> {
  const { data } = await api.post<Report>(`/report/${evidenceId}`)
  return data
}

export async function getHealth(): Promise<any> {
  const { data } = await api.get('/health')
  return data
}
