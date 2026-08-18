import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import AnalyzeMedia from './pages/AnalyzeMedia'
import Verification from './pages/Verification'
import EvidenceVault from './pages/EvidenceVault'
import Provenance from './pages/Provenance'
import Reports from './pages/Reports'
import BlockchainRecords from './pages/BlockchainRecords'
import Settings from './pages/Settings'

export default function App() {
  return (
    <div className="flex h-screen bg-navy-900 text-gray-100 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analyze" element={<AnalyzeMedia />} />
          <Route path="/verify" element={<Verification />} />
          <Route path="/vault" element={<EvidenceVault />} />
          <Route path="/provenance" element={<Provenance />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/blockchain" element={<BlockchainRecords />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}
