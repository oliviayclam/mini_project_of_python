import { useEffect, useState } from 'react'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api, clearToken, getToken } from './api'
import type { User } from './api'
import AdminPortsPage from './pages/AdminPortsPage'
import AssetsPage from './pages/AssetsPage'
import ChangeRequestsPage from './pages/ChangeRequestsPage'
import DashboardPage from './pages/DashboardPage'
import DwdmPage from './pages/DwdmPage'
import FloorPlanPage from './pages/FloorPlanPage'
import LoginPage from './pages/LoginPage'
import MasterDataPage from './pages/MasterDataPage'
import OrderDetailPage from './pages/OrderDetailPage'
import OrdersPage from './pages/OrdersPage'
import Rack2DPage from './pages/Rack2DPage'
import RacksPage from './pages/RacksPage'
import ReportsPage from './pages/ReportsPage'
import SearchPage from './pages/SearchPage'
import StructuredCablePage from './pages/StructuredCablePage'

function Shell({ user, onLogout, children }: { user: User; onLogout: () => void; children: React.ReactNode }) {
  return (
    <div className="app">
      <aside className="nav">
        <div className="brand">Network Cabling</div>
        <p className="muted small">{user.full_name} · {user.role}</p>
        <Link to="/">Dashboard</Link>
        <Link to="/search">Search</Link>
        <Link to="/racks">Racks</Link>
        <Link to="/orders">Work Orders</Link>
        <Link to="/change-requests">Change Requests</Link>
        <Link to="/floor-plan">Floor Plan</Link>
        <Link to="/assets">Create Asset</Link>
        <Link to="/structured-cables">Structured Cable</Link>
        <Link to="/master-data">Cost Centres / Floors / Rooms</Link>
        <Link to="/admin-ports">Port Remarks / Status</Link>
        <Link to="/reports">Reports / Terminate / Audit</Link>
        <Link to="/dwdm">DWDM</Link>
        <button type="button" className="secondary" onClick={onLogout}>Logout</button>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const nav = useNavigate()

  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    api<User>('/auth/me')
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false))
  }, [])

  function logout() {
    clearToken()
    setUser(null)
    nav('/login')
  }

  if (loading) return <p className="pad">Loading…</p>
  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={setUser} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Shell user={user} onLogout={logout}>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/racks" element={<RacksPage />} />
        <Route path="/racks/:id" element={<Rack2DPage />} />
        <Route path="/orders" element={<OrdersPage user={user} />} />
        <Route path="/orders/:id" element={<OrderDetailPage />} />
        <Route path="/change-requests" element={<ChangeRequestsPage user={user} />} />
        <Route path="/floor-plan" element={<FloorPlanPage />} />
        <Route path="/assets" element={<AssetsPage />} />
        <Route path="/structured-cables" element={<StructuredCablePage />} />
        <Route path="/master-data" element={<MasterDataPage />} />
        <Route path="/admin-ports" element={<AdminPortsPage />} />
        <Route path="/reports" element={<ReportsPage user={user} />} />
        <Route path="/dwdm" element={<DwdmPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  )
}
