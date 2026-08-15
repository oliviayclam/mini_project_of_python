import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { User } from '../api'

type CR = {
  id: number
  request_no: string
  change_type: string
  target_entity_type: string
  target_entity_id?: number
  proposed_changes_json: string
  status: string
  required_approvals: number
  applied: boolean
  approvals: Array<{ approver_id: number; decision: string; comment: string }>
}

export default function ChangeRequestsPage({ user }: { user: User }) {
  const [rows, setRows] = useState<CR[]>([])
  const [form, setForm] = useState({
    change_type: 'change_port',
    target_entity_type: 'port',
    target_entity_id: 1,
    required_approvals: 1,
    proposed_changes: '{"remark":"Updated via change request"}',
  })

  async function reload() {
    setRows(await api<CR[]>('/change-requests'))
  }
  useEffect(() => {
    reload().catch(console.error)
  }, [])

  async function create(e: FormEvent) {
    e.preventDefault()
    await api('/change-requests', {
      method: 'POST',
      body: JSON.stringify({
        change_type: form.change_type,
        target_entity_type: form.target_entity_type,
        target_entity_id: form.target_entity_id,
        required_approvals: form.required_approvals,
        proposed_changes: JSON.parse(form.proposed_changes),
      }),
    })
    await reload()
  }

  async function act(id: number, path: string) {
    const comment = path.includes('approve') || path.includes('reject') ? prompt('Comment') || '' : ''
    await api(`/change-requests/${id}/${path}`, {
      method: 'POST',
      body: path === 'apply' || path === 'submit' ? undefined : JSON.stringify({ comment }),
    })
    await reload()
  }

  const canApprove = user.role === 'admin' || user.role === 'operator'

  return (
    <div>
      <h1>Change Requests</h1>
      <form className="card form-grid" onSubmit={create}>
        <h2>Submit change (port/rack/replace/install)</h2>
        <label>
          Type
          <select value={form.change_type} onChange={(e) => setForm({ ...form, change_type: e.target.value })}>
            <option value="change_port">change_port</option>
            <option value="change_rack">change_rack</option>
            <option value="replace">replace</option>
            <option value="install_new">install_new</option>
          </select>
        </label>
        <label>
          Target type
          <select
            value={form.target_entity_type}
            onChange={(e) => setForm({ ...form, target_entity_type: e.target.value })}
          >
            <option value="port">port</option>
            <option value="rack">rack</option>
          </select>
        </label>
        <label>
          Target id
          <input
            type="number"
            value={form.target_entity_id}
            onChange={(e) => setForm({ ...form, target_entity_id: Number(e.target.value) })}
          />
        </label>
        <label>
          Required approvals (1-2)
          <input
            type="number"
            min={1}
            max={2}
            value={form.required_approvals}
            onChange={(e) => setForm({ ...form, required_approvals: Number(e.target.value) })}
          />
        </label>
        <label>
          Proposed changes JSON
          <textarea
            rows={3}
            value={form.proposed_changes}
            onChange={(e) => setForm({ ...form, proposed_changes: e.target.value })}
          />
        </label>
        <button type="submit">Create draft</button>
      </form>

      <table>
        <thead>
          <tr>
            <th>Request</th><th>Type</th><th>Target</th><th>Status</th><th>Approvals</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.request_no}</td>
              <td>{r.change_type}</td>
              <td>{r.target_entity_type} #{r.target_entity_id}</td>
              <td>{r.status}{r.applied ? ' (applied)' : ''}</td>
              <td>{r.approvals.filter((a) => a.decision === 'approve').length}/{r.required_approvals}</td>
              <td className="actions">
                {r.status === 'draft' && <button type="button" onClick={() => act(r.id, 'submit')}>Submit</button>}
                {['submitted', 'pending_second'].includes(r.status) && canApprove && (
                  <>
                    <button type="button" onClick={() => act(r.id, 'approve')}>Approve</button>
                    <button type="button" className="secondary" onClick={() => act(r.id, 'reject')}>Reject</button>
                  </>
                )}
                {r.status === 'approved' && !r.applied && (
                  <button type="button" onClick={() => act(r.id, 'apply')}>Apply to system</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
