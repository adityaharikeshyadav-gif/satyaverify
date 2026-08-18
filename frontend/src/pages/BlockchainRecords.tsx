import { useEffect, useState } from 'react'
import { ExternalLink, AlertTriangle } from 'lucide-react'
import { listEvidence, getBlockchainRecord } from '../services/api'
import type { Evidence } from '../types'

export default function BlockchainRecords() {
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [records, setRecords] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listEvidence().then(async (items) => {
      setEvidence(items)
      const recs: Record<string, any> = {}
      for (const item of items) {
        try {
          recs[item.evidence_id] = await getBlockchainRecord(item.evidence_id)
        } catch {
          recs[item.evidence_id] = null
        }
      }
      setRecords(recs)
      setLoading(false)
    })
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Blockchain Records</h2>
        <p className="text-navy-400 mt-1">Provenance and integrity verification records</p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-navy-400 border-b border-navy-700">
              <th className="text-left py-2">Evidence ID</th>
              <th className="text-left py-2">Filename</th>
              <th className="text-left py-2">TX Hash</th>
              <th className="text-left py-2">Contract</th>
              <th className="text-left py-2">Mode</th>
              <th className="text-left py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="py-8 text-center text-navy-400">Loading...</td></tr>
            ) : evidence.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-navy-400">No records found</td></tr>
            ) : (
              evidence.map((e) => {
                const rec = records[e.evidence_id]
                return (
                  <tr key={e.id} className="border-b border-navy-700/50 hover:bg-navy-700/20">
                    <td className="py-3 font-mono text-xs">{e.evidence_id.slice(0, 8)}</td>
                    <td className="py-3">{e.filename}</td>
                    <td className="py-3 font-mono text-xs">{rec?.tx_hash || '-'}</td>
                    <td className="py-3">{rec?.address || '-'}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${rec?.configured ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                        {rec?.demo_mode ? 'DEMO' : 'LIVE'}
                      </span>
                    </td>
                    <td className="py-3">
                      {rec?.tx_hash && <a href={`https://etherscan.io/tx/${rec.tx_hash}`} target="_blank" rel="noreferrer" className="text-accent-400 hover:text-accent-500 flex items-center gap-1"><ExternalLink size={14} /> View</a>}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="card bg-yellow-500/10 border border-yellow-500/30">
        <div className="flex items-center gap-2">
          <AlertTriangle className="text-yellow-400" size={20} />
          <p className="text-yellow-200 text-sm">
            Demo Mode: Blockchain transactions are simulated. Configure BLOCKCHAIN_RPC_URL and CONTRACT_ADDRESS for live network recording.
          </p>
        </div>
      </div>
    </div>
  )
}
