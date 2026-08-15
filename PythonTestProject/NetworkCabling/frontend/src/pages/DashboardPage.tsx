import { useEffect, useState } from 'react'
import { api } from '../api'

type Dash = {
  free_ports: number
  pending_orders: number
  approved_orders: number
  cables: number
  panels: number
}

export default function DashboardPage() {
  const [data, setData] = useState<Dash | null>(null)
  useEffect(() => {
    api<Dash>('/dashboard').then(setData).catch(console.error)
  }, [])
  if (!data) return <p>Loading…</p>
  return (
    <div>
      <h1>Dashboard</h1>
      <div className="stats">
        <div><span>Free ports</span><strong>{data.free_ports}</strong></div>
        <div><span>Pending orders</span><strong>{data.pending_orders}</strong></div>
        <div><span>Approved orders</span><strong>{data.approved_orders}</strong></div>
        <div><span>Cables</span><strong>{data.cables}</strong></div>
        <div><span>Panels</span><strong>{data.panels}</strong></div>
      </div>
    </div>
  )
}
