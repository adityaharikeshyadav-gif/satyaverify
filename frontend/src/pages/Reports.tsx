import { useState } from 'react'
import { FileText, Download, Loader2 } from 'lucide-react'
import { generateReport } from '../services/api'
import type { Report } from '../types'

export default function Reports() {
  const [evidenceId, setEvidenceId] = useState('')
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!evidenceId) return
    setLoading(true)
    setError('')
    setReport(null)
    try {
      const res = await generateReport(evidenceId)
      setReport(res)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!report) return
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report-${report.evidence_id}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-3xl font-bold text-white">Reports</h2>
        <p className="text-navy-400 mt-1">Generate and download forensic reports</p>
      </div>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-navy-300 mb-1">Evidence ID</label>
          <input className="input" value={evidenceId} onChange={(e) => setEvidenceId(e.target.value)} placeholder="Enter evidence ID" />
        </div>
        <div className="flex gap-3">
          <button onClick={handleGenerate} disabled={loading || !evidenceId} className="btn-primary flex-1 py-2 disabled:opacity-50 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="animate-spin" size={18} /> Generating...</> : <><FileText size={18} /> Generate Report</>}
          </button>
        </div>
      </div>

      {error && <div className="card border border-red-500/30 bg-red-500/10 text-red-400">{error}</div>}

      {report && (
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">Forensic Report</h3>
            <button onClick={handleDownload} className="btn-primary flex items-center gap-2">
              <Download size={18} /> Download JSON
            </button>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/30 p-3 rounded text-yellow-200 text-sm">
            {report.disclaimer}
          </div>
          <div className="space-y-3 text-sm">
            <div>
              <h4 className="text-white font-semibold">1. Evidence Information</h4>
              <p className="text-navy-300">Filename: {report.filename}</p>
              <p className="text-navy-300">Generated: {report.generated_at}</p>
            </div>
            <div>
              <h4 className="text-white font-semibold">2. File Integrity</h4>
              <p className="text-navy-300">SHA-256: <span className="font-mono text-accent-400">{report.file_integrity.sha256}</span></p>
              <p className="text-navy-300">Size: {(report.file_integrity.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <div>
              <h4 className="text-white font-semibold">3. ML Analysis</h4>
              <p className="text-navy-300">Prediction: <span className="text-white">{report.ml_analysis.prediction}</span></p>
              <p className="text-navy-300">Confidence: <span className="text-white">{report.ml_analysis.confidence}%</span></p>
            </div>
            {report.gemini_assessment && (
              <div>
                <h4 className="text-white font-semibold">4. Gemini Assessment</h4>
                <p className="text-navy-300">Assessment: <span className="text-white">{report.gemini_assessment.assessment}</span></p>
                <p className="text-navy-300">Confidence: <span className="text-white">{report.gemini_assessment.confidence}%</span></p>
                {report.gemini_assessment.observations && (
                  <ul className="list-disc list-inside text-navy-300 mt-1">
                    {report.gemini_assessment.observations.map((obs: string, i: number) => <li key={i}>{obs}</li>)}
                  </ul>
                )}
              </div>
            )}
            <div>
              <h4 className="text-white font-semibold">6. Media Metadata</h4>
              <pre className="text-navy-300 bg-navy-800/50 p-2 rounded overflow-x-auto text-xs">{JSON.stringify(report.media_metadata, null, 2)}</pre>
            </div>
            <div>
              <h4 className="text-white font-semibold">7. Blockchain Provenance</h4>
              <p className="text-navy-300">Status: <span className="text-white">{report.blockchain.status}</span></p>
              {report.blockchain.tx_hash && <p className="text-navy-300">TX: <span className="font-mono text-accent-400">{report.blockchain.tx_hash}</span></p>}
            </div>
            <div>
              <h4 className="text-white font-semibold">8. Chain of Custody</h4>
              {report.provenance.map((p, i) => (
                <div key={i} className="ml-4 border-l-2 border-navy-700 pl-3 py-1">
                  <p className="text-white text-xs font-medium">{p.event} — {new Date(p.timestamp).toLocaleString()}</p>
                  <p className="text-navy-400 text-xs">{p.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
