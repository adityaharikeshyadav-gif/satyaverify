import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Search, ShieldCheck, FolderOpen, GitBranch, FileText, Link2, Settings } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/analyze', icon: Search, label: 'Analyze Media' },
  { to: '/verify', icon: ShieldCheck, label: 'Verification' },
  { to: '/vault', icon: FolderOpen, label: 'Evidence Vault' },
  { to: '/provenance', icon: GitBranch, label: 'Provenance' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/blockchain', icon: Link2, label: 'Blockchain Records' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-navy-800 border-r border-navy-700 flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">SATYA<span className="text-accent-500">VERIFY</span></h1>
        <p className="text-xs text-navy-400 mt-1">Digital Media Forensics Platform</p>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-navy-700 text-accent-400' : 'text-navy-300 hover:bg-navy-700/50 hover:text-gray-200'
              }`
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-navy-700">
        <p className="text-xs text-navy-400">v1.0.0</p>
      </div>
    </aside>
  )
}
