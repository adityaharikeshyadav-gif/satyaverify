import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, FileType, AlertTriangle, Loader2 } from 'lucide-react'
import { analyzeMedia } from '../services/api'
import type { Evidence } from '../types'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/jpg', 'video/mp4', 'video/quicktime', 'video/x-msvideo', 'audio/wav', 'audio/mpeg', 'audio/mp3']

export default function AnalyzeMedia() {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Evidence | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setResult(null)
      setError('')
    }
  }, [])

  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setDragActive(true) }
  const handleDragLeave = () => setDragActive(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await analyzeMedia(file)
      setResult(res)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-navy-600 text-navy-300'
    if (status === 'MANIPULATED') return 'bg-red-500/20 text-red-400'
    if (status === 'SUSPICIOUS') return 'bg-yellow-500/20 text-yellow-400'
    if (status === 'VERIFIED') return 'bg-green-500/20 text-green-400'
    return 'bg-navy-600 text-navy-300'
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-3xl font-bold text-white">Analyze Media</h2>
        <p className="text-navy-400 mt-1">Upload an image, video, or audio file for forensic analysis</p>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`card border-2 border-dashed ${dragActive ? 'border-accent-500 bg-navy-800' : 'border-navy-700'} transition-colors cursor-pointer`}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <input id="file-upload" type="file" accept={ACCEPTED_TYPES.join(',')} className="hidden" onChange={handleFileChange} />
        <div className="flex flex-col items-center justify-center py-12">
          <UploadCloud className="text-navy-400 mb-4" size={48} />
          <p className="text-lg font-medium text-white">Drop your file here or click to browse</p>
          <p className="text-sm text-navy-400 mt-2">MP4, MOV, AVI, JPG, PNG, WAV, MP3</p>
          {file && (
            <div className="mt-4 flex items-center gap-2 text-accent-400">
              <FileType size={18} />
              <span className="font-medium">{file.name}</span>
              <span className="text-navy-400">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
          )}
        </div>
      </div>

      {file && !result && !loading && (
        <button onClick={handleAnalyze} className="btn-primary w-full py-3 text-lg">
          Start Analysis
        </button>
      )}

      {loading && (
        <div className="card flex items-center justify-center gap-3 py-8">
          <Loader2 className="animate-spin text-accent-500" size={24} />
          <span className="text-white font-medium">Analyzing media...</span>
        </div>
      )}

      {error && (
        <div className="card border border-red-500/30 bg-red-500/10 flex items-center gap-3">
          <AlertTriangle className="text-red-400" size={20} />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Analysis Complete</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(result.ai_prediction)}`}>
                {result.ai_prediction || 'UNVERIFIED'}
              </span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-navy-400 text-sm">File</p>
                <p className="text-white font-medium truncate">{result.filename}</p>
              </div>
              <div>
                <p className="text-navy-400 text-sm">Type</p>
                <p className="text-white font-medium capitalize">{result.media_type}</p>
              </div>
              <div>
                <p className="text-navy-400 text-sm">Confidence</p>
                <p className="text-white font-medium">{result.ai_confidence ? `${result.ai_confidence.toFixed(1)}%` : '-'}</p>
              </div>
              <div>
                <p className="text-navy-400 text-sm">Evidence ID</p>
                <p className="text-white font-mono text-xs">{result.evidence_id}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card">
              <h4 className="text-white font-semibold mb-3">Digital DNA</h4>
              <p className="text-xs text-navy-400 mb-1">SHA-256</p>
              <p className="font-mono text-xs text-accent-400 break-all">{result.sha256}</p>
              <div className="mt-3 flex gap-2">
                <button onClick={() => navigator.clipboard.writeText(result.sha256)} className="text-xs bg-navy-700 text-navy-200 px-2 py-1 rounded">Copy Hash</button>
              </div>
            </div>
            <div className="card">
              <h4 className="text-white font-semibold mb-3">Model Scores</h4>
              {result.model_scores ? (
                <div className="space-y-2">
                  {Object.entries(result.model_scores).map(([model, score]) => (
                    <div key={model} className="flex justify-between text-sm">
                      <span className="text-navy-300 capitalize">{model.replace('_', ' ')}</span>
                      <span className="text-white font-mono">{typeof score === 'number' ? `${score.toFixed(1)}%` : score}</span>
                    </div>
                  ))}
                </div>
              ) : <p className="text-navy-400 text-sm">No model scores available</p>}
            </div>
          </div>

          {result.suspicious_frames && result.suspicious_frames.length > 0 && (
            <div className="card">
              <h4 className="text-white font-semibold mb-3">Suspicious Frames</h4>
              <div className="space-y-2">
                {result.suspicious_frames.map((f, i) => (
                  <div key={i} className="flex items-center justify-between bg-navy-800/50 px-3 py-2 rounded">
                    <span className="text-navy-300 text-sm">Frame {f.frame_number}</span>
                    <span className="text-navy-400 text-xs">Timestamp: {f.timestamp}s</span>
                    <span className="text-yellow-400 text-sm">{f.prediction}</span>
                    <span className="text-white font-mono text-sm">{f.confidence.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => navigate(`/provenance?id=${result.evidence_id}`)} className="btn-primary flex-1 py-2">
              View Provenance
            </button>
            <button onClick={() => navigate(`/reports?id=${result.evidence_id}`)} className="btn-primary flex-1 py-2 bg-navy-700 hover:bg-navy-600">
              Generate Report
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
