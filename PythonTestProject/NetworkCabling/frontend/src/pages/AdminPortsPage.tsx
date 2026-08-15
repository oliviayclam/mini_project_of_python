import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'

export default function AdminPortsPage() {
  const [ports, setPorts] = useState<any[]>([])
  const [statuses, setStatuses] = useState<any[]>([])
  const [selected, setSelected] = useState(0)
  const [remark, setRemark] = useState('')
  const [statusId, setStatusId] = useState(0)
  const [newStatus, setNewStatus] = useState({ name: '', color_hex: '#22c55e' })

  async function reload() {
    const [p, s] = await Promise.all([api<any[]>('/ports'), api<any[]>('/port-statuses')])
    setPorts(p)
    setStatuses(s)
    if (!selected && p[0]) {
      setSelected(p[0].id)
      setRemark(p[0].remark || '')
      setStatusId(p[0].status_id || s[0]?.id || 0)
    }
  }
  useEffect(() => {
    reload().catch(console.error)
  }, [])

  async function saveRemark(e: FormEvent) {
    e.preventDefault()
    await api(`/ports/${selected}/remark`, { method: 'PATCH', body: JSON.stringify({ remark }) })
    await reload()
  }

  async function saveStatus(e: FormEvent) {
    e.preventDefault()
    await api(`/ports/${selected}/status`, { method: 'PATCH', body: JSON.stringify({ status_id: statusId }) })
    await reload()
  }

  async function createStatus(e: FormEvent) {
    e.preventDefault()
    await api('/port-statuses', { method: 'POST', body: JSON.stringify(newStatus) })
    setNewStatus({ name: '', color_hex: '#22c55e' })
    await reload()
  }

  async function updateStatusColor(id: number, color_hex: string, name: string, is_system_status: boolean) {
    await api(`/port-statuses/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name, color_hex, is_system_status }),
    })
    await reload()
  }

  return (
    <div>
      <h1>Port Remarks & Status</h1>
      <div className="two-col">
        <form className="card form-grid" onSubmit={saveRemark}>
          <h2>Review / edit remark</h2>
          <label>
            Port
            <select
              value={selected}
              onChange={(e) => {
                const id = Number(e.target.value)
                setSelected(id)
                const p = ports.find((x) => x.id === id)
                setRemark(p?.remark || '')
                setStatusId(p?.status_id || 0)
              }}
            >
              {ports.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <label>
            Remark
            <textarea value={remark} onChange={(e) => setRemark(e.target.value)} rows={3} />
          </label>
          <button type="submit">Save remark</button>
        </form>

        <form className="card form-grid" onSubmit={saveStatus}>
          <h2>Update port status</h2>
          <label>
            Status
            <select value={statusId} onChange={(e) => setStatusId(Number(e.target.value))}>
              {statuses.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </label>
          <button type="submit">Update status</button>
        </form>
      </div>

      <div className="card">
        <h2>Status colors (pick color)</h2>
        <table>
          <thead><tr><th>Name</th><th>Color</th><th>Preview</th></tr></thead>
          <tbody>
            {statuses.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>
                  <input
                    type="color"
                    value={s.color_hex}
                    onChange={(e) => updateStatusColor(s.id, e.target.value, s.name, s.is_system_status)}
                  />
                </td>
                <td><span className="swatch" style={{ background: s.color_hex }} /> {s.color_hex}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form className="form-grid" onSubmit={createStatus}>
          <h3>Add status</h3>
          <label>Name <input value={newStatus.name} onChange={(e) => setNewStatus({ ...newStatus, name: e.target.value })} required /></label>
          <label>Color <input type="color" value={newStatus.color_hex} onChange={(e) => setNewStatus({ ...newStatus, color_hex: e.target.value })} /></label>
          <button type="submit">Create status</button>
        </form>
      </div>
    </div>
  )
}
