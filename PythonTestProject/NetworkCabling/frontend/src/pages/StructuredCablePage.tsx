import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'

export default function StructuredCablePage() {
  const [ports, setPorts] = useState<any[]>([])
  const [types, setTypes] = useState<any[]>([])
  const [services, setServices] = useState<any[]>([])
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({
    cable_type_id: 0,
    service_type_id: 0,
    a_port_id: 0,
    b_port_id: 0,
    b_customer_name: '',
    length_m: 10,
    label: '',
    notes: '',
  })

  useEffect(() => {
    Promise.all([api<any[]>('/ports'), api<any[]>('/cable-types'), api<any[]>('/service-types')]).then(
      ([p, t, s]) => {
        setPorts(p); setTypes(t); setServices(s)
        setForm((f) => ({
          ...f,
          a_port_id: p[0]?.id || 0,
          b_port_id: p[1]?.id || 0,
          cable_type_id: t[0]?.id || 0,
          service_type_id: s[0]?.id || 0,
        }))
      },
    )
  }, [])

  async function submit(e: FormEvent) {
    e.preventDefault()
    const body = {
      ...form,
      b_port_id: form.b_customer_name ? null : form.b_port_id || null,
    }
    await api('/structured-cables', { method: 'POST', body: JSON.stringify(body) })
    setMsg('Structured cable created')
  }

  return (
    <div>
      <h1>Create Structured Cable</h1>
      {msg && <p className="ok">{msg}</p>}
      <form className="card form-grid" onSubmit={submit}>
        <label>From panel port
          <select value={form.a_port_id} onChange={(e) => setForm({ ...form, a_port_id: Number(e.target.value) })}>
            {ports.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
        <label>To panel port (optional)
          <select value={form.b_port_id} onChange={(e) => setForm({ ...form, b_port_id: Number(e.target.value) })}>
            <option value={0}>Customer endpoint instead</option>
            {ports.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
        <label>Or customer name
          <input value={form.b_customer_name} onChange={(e) => setForm({ ...form, b_customer_name: e.target.value })} />
        </label>
        <label>Cable type
          <select value={form.cable_type_id} onChange={(e) => setForm({ ...form, cable_type_id: Number(e.target.value) })}>
            {types.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </label>
        <label>Service type
          <select value={form.service_type_id} onChange={(e) => setForm({ ...form, service_type_id: Number(e.target.value) })}>
            {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </label>
        <label>Length (m)
          <input type="number" value={form.length_m} onChange={(e) => setForm({ ...form, length_m: Number(e.target.value) })} />
        </label>
        <label>Label <input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} /></label>
        <button type="submit">Create</button>
      </form>
    </div>
  )
}
