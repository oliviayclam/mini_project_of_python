import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'

export default function AssetsPage() {
  const [masters, setMasters] = useState<any>({})
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({
    kind: 'odf',
    cost_centre_id: 0,
    floor_id: 0,
    room_id: 0,
    rack_id: 0,
    name: '',
    shelf_or_u: 40,
    port_count: 24,
    asset_type: 'ODF',
    rack_type: 'Shelf',
    manufacturer: '',
    model: '',
    serial_number: '',
    install_date: '',
    expire_date: '',
    asset_tag: '',
    notes: '',
  })

  useEffect(() => {
    Promise.all([
      api<any[]>('/cost-centres'),
      api<any[]>('/floors'),
      api<any[]>('/rooms'),
      api<any[]>('/racks'),
    ]).then(([cc, floors, rooms, racks]) => {
      setMasters({ cc, floors, rooms, racks })
      setForm((f) => ({
        ...f,
        cost_centre_id: cc[0]?.id || 0,
        floor_id: floors[0]?.id || 0,
        room_id: rooms[0]?.id || 0,
        rack_id: racks[0]?.id || 0,
      }))
    })
  }, [])

  async function submit(e: FormEvent) {
    e.preventDefault()
    setMsg('')
    const path =
      form.kind === 'odf' ? '/assets/odf-racks' : form.kind === 'shelf' ? '/assets/shelves' : '/assets/panels'
    const body = {
      ...form,
      install_date: form.install_date || null,
      expire_date: form.expire_date || null,
      rack_id: form.kind === 'odf' ? null : form.rack_id,
    }
    await api(path, { method: 'POST', body: JSON.stringify(body) })
    setMsg(`${form.kind} created`)
  }

  return (
    <div>
      <h1>Create Asset</h1>
      {msg && <p className="ok">{msg}</p>}
      <form className="card form-grid" onSubmit={submit}>
        <label>
          Asset
          <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
            <option value="odf">ODF (Rack)</option>
            <option value="shelf">Shelf</option>
            <option value="panel">Panel</option>
          </select>
        </label>
        <label>Name <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
        <label>
          Cost centre
          <select value={form.cost_centre_id} onChange={(e) => setForm({ ...form, cost_centre_id: Number(e.target.value) })}>
            {(masters.cc || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Floor
          <select value={form.floor_id} onChange={(e) => setForm({ ...form, floor_id: Number(e.target.value) })}>
            {(masters.floors || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Room
          <select value={form.room_id} onChange={(e) => setForm({ ...form, room_id: Number(e.target.value) })}>
            {(masters.rooms || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        {form.kind !== 'odf' && (
          <label>
            Rack
            <select value={form.rack_id} onChange={(e) => setForm({ ...form, rack_id: Number(e.target.value) })}>
              {(masters.racks || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
            </select>
          </label>
        )}
        <label>Shelf / U <input type="number" value={form.shelf_or_u} onChange={(e) => setForm({ ...form, shelf_or_u: Number(e.target.value) })} /></label>
        <label>Port count <input type="number" value={form.port_count} onChange={(e) => setForm({ ...form, port_count: Number(e.target.value) })} /></label>
        <label>Manufacturer <input value={form.manufacturer} onChange={(e) => setForm({ ...form, manufacturer: e.target.value })} /></label>
        <label>Model <input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} /></label>
        <label>Serial <input value={form.serial_number} onChange={(e) => setForm({ ...form, serial_number: e.target.value })} /></label>
        <label>Install date <input type="date" value={form.install_date} onChange={(e) => setForm({ ...form, install_date: e.target.value })} /></label>
        <label>Expire date <input type="date" value={form.expire_date} onChange={(e) => setForm({ ...form, expire_date: e.target.value })} /></label>
        <label>Asset tag <input value={form.asset_tag} onChange={(e) => setForm({ ...form, asset_tag: e.target.value })} /></label>
        <label>Notes <input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
        <button type="submit">Create</button>
      </form>
    </div>
  )
}
