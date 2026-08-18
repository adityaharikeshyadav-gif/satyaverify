import { useEffect, useState } from 'react'
import { getHealth } from '../services/api'

export default function Settings() {
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-3xl font-bold text-white">Settings</h2>
        <p className="text-navy-400 mt-1">System configuration and status</p>
      </div>

      <div className="card space-y-3">
        <h3 className="text-lg font-semibold text-white">System Status</h3>
        {health && (
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-navy-400">Status:</span> <span className="text-green-400 font-medium">{health.status}</span></div>
            <div><span className="text-navy-400">Demo Mode:</span> <span className="text-white">{health.demo_mode ? 'Yes' : 'No'}</span></div>
            <div><span className="text-navy-400">Network:</span> <span className="text-white">{health.blockchain?.network || 'N/A'}</span></div>
            <div><span className="text-navy-400">Contract:</span> <span className="text-white">{health.blockchain?.configured ? 'Configured' : 'Not configured'}</span></div>
          </div>
        )}
      </div>

      <div className="card space-y-3">
        <h3 className="text-lg font-semibold text-white">Configuration</h3>
        <div className="text-sm text-navy-300 space-y-2">
          <p><span className="text-navy-400">Backend:</span> <span className="text-white">http://localhost:8000</span></p>
          <p><span className="text-navy-400">Frontend:</span> <span className="text-white">http://localhost:5173</span></p>
          <p><span className="text-navy-400">Database:</span> <span className="text-white">PostgreSQL (localhost:5432)</span></p>
          <p><span className="text-navy-400">ML Models:</span> <span className="text-white">Random Forest, XGBoost, SVM</span></p>
          <p><span className="text-navy-400">AI:</span> <span className="text-white">Gemini API</span></p>
        </div>
      </div>
    </div>
  )
}
