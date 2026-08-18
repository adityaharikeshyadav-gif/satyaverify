import { useEffect, useState } from 'react'
import { listEvidence } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Upload, ShieldAlert, CheckCircle, FileWarning } from 'lucide-react'
import type { Evidence } from '../types'

const COLORS = ['#0ea5e9', '#ef4444', '#22c55e', '#f59e0b']

export default function Dashboard() {
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listEvidence().then(setEvidence).finally(() => setLoading(false))
  }, [])

  const stats = {
    total: evidence.length,
    deepfakes: evidence.filter(e => e.ai_prediction === 'MANIPULATED').length,
    verified: evidence.filter(e => e.ai_prediction === 'VERIFIED').length,
    alerts: evidence.filter(e => e.ai_prediction === 'SUSPICIOUS').length,
  }

  const predictionData = [
    { name: 'Verified', value: stats.verified },
    { name: 'Suspicious', value: stats.alerts },
    { name: 'Manipulated', value: stats.deepfakes },
    { name: 'Unverified', value: stats.total - stats.verified - stats.alerts - stats.deepfakes },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Dashboard</h2>
        <p className="text-navy-400 mt-1">Digital media forensics overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card flex items-center gap-4">
          <Upload className="text-accent-500" size={28} />
          <div>
            <p className="text-2xl font-bold text-white">{stats.total}</p>
            <p className="text-sm text-navy-400">Total Media Analyzed</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <ShieldAlert className="text-red-400" size={28} />
          <div>
            <p className="text-2xl font-bold text-white">{stats.deepfakes}</p>
            <p className="text-sm text-navy-400">Potential Deepfakes</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <CheckCircle className="text-green-400" size={28} />
          <div>
            <p className="text-2xl font-bold text-white">{stats.verified}</p>
            <p className="text-sm text-navy-400">Verified Media</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <FileWarning className="text-yellow-400" size={28} />
          <div>
            <p className="text-2xl font-bold text-white">{stats.alerts}</p>
            <p className="text-sm text-navy-400">Integrity Alerts</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Detection Confidence</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={evidence.slice(0, 10).map(e => ({ name: e.filename.slice(0, 15), confidence: e.ai_confidence || 0 }))}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#e2e8f0' }} />
              <Bar dataKey="confidence" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Real vs Suspicious</h3>
          <ResponsiveContainer width="100%" height={250}>
              <PieChart>
              <Pie data={predictionData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label>
                {predictionData.map((_entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#e2e8f0' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Investigations</h3>
        {loading ? (
          <p className="text-navy-400">Loading...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-navy-400 border-b border-navy-700">
                  <th className="text-left py-2">Evidence ID</th>
                  <th className="text-left py-2">Filename</th>
                  <th className="text-left py-2">Type</th>
                  <th className="text-left py-2">AI Result</th>
                  <th className="text-left py-2">Confidence</th>
                  <th className="text-left py-2">Integrity</th>
                  <th className="text-left py-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {evidence.slice(0, 10).map((e) => (
                  <tr key={e.id} className="border-b border-navy-700/50 hover:bg-navy-700/20">
                    <td className="py-3 font-mono text-xs">{e.evidence_id.slice(0, 8)}</td>
                    <td className="py-3">{e.filename}</td>
                    <td className="py-3 capitalize">{e.media_type}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        e.ai_prediction === 'MANIPULATED' ? 'bg-red-500/20 text-red-400' :
                        e.ai_prediction === 'SUSPICIOUS' ? 'bg-yellow-500/20 text-yellow-400' :
                        e.ai_prediction === 'VERIFIED' ? 'bg-green-500/20 text-green-400' :
                        'bg-navy-600 text-navy-300'
                      }`}>
                        {e.ai_prediction || 'UNVERIFIED'}
                      </span>
                    </td>
                    <td className="py-3">{e.ai_confidence ? `${e.ai_confidence.toFixed(1)}%` : '-'}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        e.blockchain_tx_hash ? 'bg-green-500/20 text-green-400' : 'bg-navy-600 text-navy-300'
                      }`}>
                        {e.blockchain_tx_hash ? 'VERIFIED' : 'PENDING'}
                      </span>
                    </td>
                    <td className="py-3 text-navy-300">{new Date(e.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
