import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { GitBranch, Clock, CheckCircle, AlertTriangle } from 'lucide-react'
import { getProvenance, getEvidence } from '../services/api'
import type { ProvenanceEvent, Evidence } from '../types'

export default function Provenance() {
  const [searchParams] = useSearchParams()
  const initialId = searchParams.get('id') || ''
  const [evidenceId, setEvidenceId] = useState(initialId)
  const [events, setEvents] = useState<ProvenanceEvent[]>([])
  const [evidence, setEvidence] = useState<Evidence | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (initialId) {
      handleSearch(initialId)
    }
  }, [initialId])

  const handleSearch = async (id?: string) => {
    const targetId = id || evidenceId
    if (!targetId) return
    setLoading(true)
    try {
      const ev = await getEvidence(targetId)
      setEvidence(ev)
      const prov = await getProvenance(targetId)
      setEvents(prov)
    } catch {
      setEvidence(null)
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  const getEventIcon = (type: string) => {
    if (type === 'REGISTERED') return <Clock className="text-accent-500" size={18} />
    if (type === 'ANALYZED') return <CheckCircle className="text-green-400" size={18} />
    if (type === 'VERIFIED') return <CheckCircle className="text-green-400" size={18} />
    if (type === 'TRANSFERRED') return <GitBranch className="text-yellow-400" size={18} />
    return <AlertTriangle className="text-navy-400" size={18} />
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-3xl font-bold text-white">Provenance</h2>
        <p className="text-navy-400 mt-1">Chain of custody and evidence history</p>
      </div>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-navy-300 mb-1">Evidence ID</label>
          <input className="input" value={evidenceId} onChange={(e) => setEvidenceId(e.target.value)} placeholder="Enter evidence ID" />
        </div>
        <button onClick={() => handleSearch()} disabled={loading || !evidenceId} className="btn-primary w-full py-2 disabled:opacity-50">
          {loading ? 'Loading...' : 'Load Provenance'}
        </button>
      </div>

      {evidence && (
        <div className="card space-y-4">
          <div className="flex items-center gap-3">
            <GitBranch className="text-accent-500" size={24} />
            <div>
              <h3 className="text-lg font-semibold text-white">Evidence: {evidence.filename}</h3>
              <p className="text-xs text-navy-400 font-mono">{evidence.evidence_id}</p>
            </div>
          </div>
          <div className="relative border-l-2 border-navy-700 ml-4 pl-6 space-y-6">
            {events.length === 0 ? (
              <p className="text-navy-400 text-sm">No provenance events recorded.</p>
            ) : (
              events.map((ev) => (
                <div key={ev.id} className="relative">
                  <div className="absolute -left-[31px] top-1">{getEventIcon(ev.event_type)}</div>
                  <div className="bg-navy-800/50 p-3 rounded">
                    <div className="flex items-center justify-between">
                      <span className="text-white font-medium">{ev.event_type}</span>
                      <span className="text-xs text-navy-400">{new Date(ev.timestamp).toLocaleString()}</span>
                    </div>
                    {ev.description && <p className="text-sm text-navy-300 mt-1">{ev.description}</p>}
                    <p className="text-xs text-navy-400 mt-1">Actor: {ev.actor}</p>
                    {ev.tx_hash && <p className="text-xs text-accent-400 font-mono mt-1">TX: {ev.tx_hash}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
