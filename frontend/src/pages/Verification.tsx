import { useState } from 'react'
import { ShieldCheck, CheckCircle, AlertTriangle } from 'lucide-react'
import { verifyEvidence } from '../services/api'

export default function Verification() {
  const [evidenceId, setEvidenceId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerify = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await verifyEvidence(evidenceId || undefined, file || undefined)
      setResult(res)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-3xl font-bold text-white">Verification</h2>
        <p className="text-navy-400 mt-1">Verify file integrity and check against registered evidence</p>
      </div>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-navy-300 mb-1">Evidence ID</label>
          <input className="input" value={evidenceId} onChange={(e) => setEvidenceId(e.target.value)} placeholder="Enter evidence ID" />
        </div>
        <div>
          <label className="block text-sm font-medium text-navy-300 mb-1">Or Upload File</label>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="input" />
        </div>
        <button onClick={handleVerify} disabled={loading || (!evidenceId && !file)} className="btn-primary w-full py-3 disabled:opacity-50">
          {loading ? 'Verifying...' : 'Verify'}
        </button>
      </div>

      {error && (
        <div className="card border border-red-500/30 bg-red-500/10 flex items-center gap-3">
          <AlertTriangle className="text-red-400" size={20} />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {result && (
        <div className="card space-y-3">
          <div className="flex items-center gap-3">
            {result.status === 'HASH_MATCH' ? <CheckCircle className="text-green-400" size={24} /> : <ShieldCheck className="text-accent-500" size={24} />}
            <h3 className="text-xl font-bold text-white">{result.status.replace('_', ' ')}</h3>
          </div>
          <p className="text-navy-300 text-sm">{result.message}</p>
          {result.sha256 && (
            <div>
              <p className="text-xs text-navy-400">SHA-256</p>
              <p className="font-mono text-xs text-accent-400 break-all">{result.sha256}</p>
            </div>
          )}
          {result.evidence && (
            <div className="bg-navy-800/50 p-3 rounded text-sm space-y-1">
              <p><span className="text-navy-400">File:</span> <span className="text-white">{result.evidence.filename}</span></p>
              <p><span className="text-navy-400">AI Result:</span> <span className="text-white">{result.evidence.ai_prediction}</span></p>
              <p><span className="text-navy-400">Confidence:</span> <span className="text-white">{result.evidence.ai_confidence?.toFixed(1)}%</span></p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
