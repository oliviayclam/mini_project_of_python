import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { User } from '../api'

type Order = {
  id: number
  request_no: string
  vendor_id: number
  cost_centre_id: number
  status: string
  remarks: string
  approver_comment: string
  lines: Array<{
    id: number
    endpoint_a: string
    endpoint_b: string
    requested_length_m: number
    cable_type_id?: number
    path_group: string
    path_index: number
  }>
}
type CC = { id: number; name: string }
type CT = { id: number; name: string }
type ST = { id: number; name: string }
type Suggestion = {
  cable_type_id?: number
  cable_type_name?: string
  service_type_id?: number
  service_type_name?: string
  estimated_length_m: number
  notes: string
}

export default function OrdersPage({ user }: { user: User }) {
  const [orders, setOrders] = useState<Order[]>([])
  const [ccs, setCcs] = useState<CC[]>([])
  const [types, setTypes] = useState<CT[]>([])
  const [services, setServices] = useState<ST[]>([])
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({
    cost_centre_id: 0,
    remarks: '',
    endpoint_a: '',
    endpoint_b: '',
    cable_type_id: 0,
    service_type_id: 0,
    requested_length_m: 10,
  })

  async function reload() {
    const [o, c, t, s] = await Promise.all([
      api<Order[]>('/orders'),
      api<CC[]>('/cost-centres'),
      api<CT[]>('/cable-types'),
      api<ST[]>('/service-types'),
    ])
    setOrders(o)
    setCcs(c)
    setTypes(t)
    setServices(s)
    setForm((f) => ({
      ...f,
      cost_centre_id: f.cost_centre_id || c[0]?.id || 0,
      cable_type_id: f.cable_type_id || t[0]?.id || 0,
      service_type_id: f.service_type_id || s[0]?.id || 0,
    }))
  }

  useEffect(() => {
    reload().catch(console.error)
  }, [])

  async function createDraft(e: FormEvent) {
    e.preventDefault()
    setMsg('')
    await api('/orders', {
      method: 'POST',
      body: JSON.stringify({
        cost_centre_id: form.cost_centre_id,
        remarks: form.remarks,
        lines: [
          {
            line_no: 1,
            path_group: 'A',
            path_index: 1,
            endpoint_a: form.endpoint_a,
            endpoint_b: form.endpoint_b,
            cable_type_id: form.cable_type_id,
            service_type_id: form.service_type_id,
            requested_length_m: form.requested_length_m,
          },
        ],
      }),
    })
    setMsg('Draft order created')
    await reload()
  }

  async function submit(id: number) {
    await api(`/orders/${id}/submit`, { method: 'POST' })
    await reload()
  }

  async function decide(id: number, action: 'approve' | 'reject') {
    const comment = prompt('Comment') || ''
    await api(`/orders/${id}/${action}`, { method: 'POST', body: JSON.stringify({ comment }) })
    await reload()
  }

  async function loadSuggestions(id: number) {
    const s = await api<Suggestion>(`/orders/${id}/suggestions`)
    setMsg(
      `Suggestion: ${s.cable_type_name || '-'} / ${s.service_type_name || '-'} / ${s.estimated_length_m}m — ${s.notes}`,
    )
  }

  const canCreate = user.role === 'vendor' || user.role === 'admin'
  const canApprove = user.role === 'operator' || user.role === 'admin'

  return (
    <div>
      <h1>Work Orders</h1>
      {msg && <p className="ok">{msg}</p>}
      {canCreate && (
        <form className="card form-grid" onSubmit={createDraft}>
          <h2>New draft order (1+ full paths)</h2>
          <label>
            Cost centre
            <select
              value={form.cost_centre_id}
              onChange={(e) => setForm({ ...form, cost_centre_id: Number(e.target.value) })}
            >
              {ccs.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </label>
          <label>
            Cable type
            <select
              value={form.cable_type_id}
              onChange={(e) => setForm({ ...form, cable_type_id: Number(e.target.value) })}
            >
              {types.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </label>
          <label>
            Service type
            <select
              value={form.service_type_id}
              onChange={(e) => setForm({ ...form, service_type_id: Number(e.target.value) })}
            >
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </label>
          <label>
            From
            <input value={form.endpoint_a} onChange={(e) => setForm({ ...form, endpoint_a: e.target.value })} required />
          </label>
          <label>
            To (panel / customer)
            <input value={form.endpoint_b} onChange={(e) => setForm({ ...form, endpoint_b: e.target.value })} required />
          </label>
          <label>
            Length (m)
            <input
              type="number"
              value={form.requested_length_m}
              onChange={(e) => setForm({ ...form, requested_length_m: Number(e.target.value) })}
            />
          </label>
          <label>
            Remarks
            <input value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
          </label>
          <button type="submit">Create draft</button>
        </form>
      )}

      <table>
        <thead>
          <tr>
            <th>Request</th><th>Status</th><th>Lines</th><th>Remarks</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td><Link to={`/orders/${o.id}`}>{o.request_no}</Link></td>
              <td>{o.status}</td>
              <td>{o.lines.length}</td>
              <td>{o.remarks}</td>
              <td className="actions">
                {o.status === 'draft' && canCreate && (
                  <>
                    <button type="button" onClick={() => loadSuggestions(o.id)}>Suggest</button>
                    <button type="button" onClick={() => submit(o.id)}>Submit</button>
                  </>
                )}
                {o.status === 'submitted' && canApprove && (
                  <>
                    <button type="button" onClick={() => decide(o.id, 'approve')}>Approve</button>
                    <button type="button" className="secondary" onClick={() => decide(o.id, 'reject')}>Reject</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
