import { useEffect, useState } from 'react'
import { listEvidence } from '../services/api'
import { Search } from 'lucide-react'
import type { Evidence } from '../types'

export default function EvidenceVault() {
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [filter, setFilter] = useState('')
  const [selected, setSelected] = useState<Evidence | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listEvidence().then(setEvidence).finally(() => setLoading(false))
  }, [])

  const filtered = evidence.filter(e =>
    e.filename.toLowerCase().includes(filter.toLowerCase()) ||
    e.evidence_id.toLowerCase().includes(filter.toLowerCase()) ||
    e.ai_prediction?.toLowerCase().includes(filter.toLowerCase())
  )

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-navy-600 text-navy-300'
    if (status === 'MANIPULATED') return 'bg-red-500/20 text-red-400'
    if (status === 'SUSPICIOUS') return 'bg-yellow-500/20 text-yellow-400'
    if (status === 'VERIFIED') return 'bg-green-500/20 text-green-400'
    return 'bg-navy-600 text-navy-300'
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Evidence Vault</h2>
        <p className="text-navy-400 mt-1">Browse and search registered evidence</p>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 text-navy-400" size={18} />
          <input className="input pl-10" placeholder="Search by filename, ID, or status..." value={filter} onChange={(e) => setFilter(e.target.value)} />
        </div>
      </div>

      {selected && (
        <div className="card space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-white">Evidence Details</h3>
            <button onClick={() => setSelected(null)} className="text-navy-400 hover:text-white text-sm">Close</button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div><span className="text-navy-400">Filename:</span> <span className="text-white">{selected.filename}</span></div>
            <div><span className="text-navy-400">Type:</span> <span className="text-white capitalize">{selected.media_type}</span></div>
            <div><span className="text-navy-400">Size:</span> <span className="text-white">{(selected.size / 1024 / 1024).toFixed(2)} MB</span></div>
            <div><span className="text-navy-400">SHA-256:</span> <span className="text-accent-400 font-mono text-xs break-all">{selected.sha256}</span></div>
            <div><span className="text-navy-400">AI Prediction:</span> <span className={`px-2 py-0.5 rounded text-xs ${getStatusColor(selected.ai_prediction)}`}>{selected.ai_prediction}</span></div>
            <div><span className="text-navy-400">Confidence:</span> <span className="text-white">{selected.ai_confidence?.toFixed(1)}%</span></div>
            <div><span className="text-navy-400">Status:</span> <span className="text-white">{selected.status}</span></div>
            <div><span className="text-navy-400">Blockchain:</span> <span className="text-white">{selected.blockchain_tx_hash ? 'Recorded' : 'None'}</span></div>
          </div>
        </div>
      )}

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-navy-400 border-b border-navy-700">
              <th className="text-left py-2">Evidence ID</th>
              <th className="text-left py-2">Filename</th>
              <th className="text-left py-2">Type</th>
              <th className="text-left py-2">AI Result</th>
              <th className="text-left py-2">Confidence</th>
              <th className="text-left py-2">Status</th>
              <th className="text-left py-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="py-8 text-center text-navy-400">Loading...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={7} className="py-8 text-center text-navy-400">No evidence found</td></tr>
            ) : (
              filtered.map((e) => (
                <tr key={e.id} className="border-b border-navy-700/50 hover:bg-navy-700/20 cursor-pointer" onClick={() => setSelected(e)}>
                  <td className="py-3 font-mono text-xs">{e.evidence_id.slice(0, 8)}</td>
                  <td className="py-3">{e.filename}</td>
                  <td className="py-3 capitalize">{e.media_type}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(e.ai_prediction)}`}>
                      {e.ai_prediction || 'UNVERIFIED'}
                    </span>
                  </td>
                  <td className="py-3">{e.ai_confidence ? `${e.ai_confidence.toFixed(1)}%` : '-'}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${e.blockchain_tx_hash ? 'bg-green-500/20 text-green-400' : 'bg-navy-600 text-navy-300'}`}>
                      {e.blockchain_tx_hash ? 'VERIFIED' : 'PENDING'}
                    </span>
                  </td>
                  <td className="py-3 text-navy-300">{new Date(e.created_at).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
