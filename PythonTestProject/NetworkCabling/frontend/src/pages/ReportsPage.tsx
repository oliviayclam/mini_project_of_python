import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { User } from '../api'

const REPORTS = [
  ['invoice', 'Invoice report'],
  ['inspection', 'Inspection report'],
  ['termination', 'Termination report'],
  ['cabling-mark-area', 'Cabling mark area'],
  ['exception', 'Exception report'],
  ['structured-cable', 'Structured cable report'],
  ['odf-patch-utilization', 'ODF / Patch utilization'],
] as const

export default function ReportsPage({ user }: { user: User }) {
  const [report, setReport] = useState('odf-patch-utilization')
  const [data, setData] = useState<any>(null)
  const [terms, setTerms] = useState<any[]>([])
  const [cables, setCables] = useState<any[]>([])
  const [termForm, setTermForm] = useState({ cable_id: 0, reason: '' })
  const [logs, setLogs] = useState<any[]>([])

  useEffect(() => {
    api<any[]>('/cables').then((c) => {
      setCables(c)
      setTermForm((f) => ({ ...f, cable_id: c[0]?.id || 0 }))
    })
    api<any[]>('/termination-requests').then(setTerms).catch(console.error)
  }, [])

  async function loadReport() {
    if (report === 'invoice' && !['admin', 'department_admin'].includes(user.role)) {
      setData({ error: 'department_admin or admin required' })
      return
    }
    setData(await api(`/reports/${report}`))
  }

  async function createTerm(e: FormEvent) {
    e.preventDefault()
    await api('/termination-requests', { method: 'POST', body: JSON.stringify(termForm) })
    setTerms(await api('/termination-requests'))
  }

  async function decideTerm(id: number, action: 'approve' | 'reject') {
    const comment = prompt('Comment') || ''
    await api(`/termination-requests/${id}/${action}`, { method: 'POST', body: JSON.stringify({ comment }) })
    setTerms(await api('/termination-requests'))
  }

  async function loadLogs() {
    setLogs(await api('/audit-logs'))
  }

  async function exportLogs() {
    const token = localStorage.getItem('token')
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/audit-logs/export?format=csv`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'audit_logs.csv'
    a.click()
  }

  return (
    <div>
      <h1>Reports & Termination & Audit</h1>
      <div className="card form-grid">
        <label>
          Report
          <select value={report} onChange={(e) => setReport(e.target.value)}>
            {REPORTS.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
          </select>
        </label>
        <button type="button" onClick={loadReport}>Run report</button>
      </div>
      {data && <pre className="code-block">{JSON.stringify(data, null, 2)}</pre>}

      <form className="card form-grid" onSubmit={createTerm}>
        <h2>Request Terminate</h2>
        <label>
          Cable
          <select value={termForm.cable_id} onChange={(e) => setTermForm({ ...termForm, cable_id: Number(e.target.value) })}>
            {cables.map((c) => <option key={c.id} value={c.id}>{c.label || c.id}</option>)}
          </select>
        </label>
        <label>Reason <input value={termForm.reason} onChange={(e) => setTermForm({ ...termForm, reason: e.target.value })} /></label>
        <button type="submit">Submit termination</button>
      </form>
      <table>
        <thead><tr><th>Request</th><th>Status</th><th>Reason</th><th>Actions</th></tr></thead>
        <tbody>
          {terms.map((t) => (
            <tr key={t.id}>
              <td>{t.request_no}</td>
              <td>{t.status}</td>
              <td>{t.reason}</td>
              <td className="actions">
                {t.status === 'submitted' && (user.role === 'admin' || user.role === 'operator') && (
                  <>
                    <button type="button" onClick={() => decideTerm(t.id, 'approve')}>Approve</button>
                    <button type="button" className="secondary" onClick={() => decideTerm(t.id, 'reject')}>Reject</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {user.role === 'admin' && (
        <div className="card">
          <h2>Audit logs</h2>
          <div className="actions">
            <button type="button" onClick={loadLogs}>Load</button>
            <button type="button" className="secondary" onClick={exportLogs}>Export CSV</button>
          </div>
          <table>
            <thead><tr><th>ID</th><th>User</th><th>Action</th><th>Entity</th><th>When</th></tr></thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id}>
                  <td>{l.id}</td>
                  <td>{l.user_id} ({l.role})</td>
                  <td>{l.action}</td>
                  <td>{l.entity_type} {l.entity_id}</td>
                  <td>{l.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
