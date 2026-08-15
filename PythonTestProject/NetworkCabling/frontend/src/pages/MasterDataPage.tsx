import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'

export default function MasterDataPage() {
  const [ccs, setCcs] = useState<any[]>([])
  const [floors, setFloors] = useState<any[]>([])
  const [rooms, setRooms] = useState<any[]>([])
  const [sites, setSites] = useState<any[]>([])
  const [ccForm, setCcForm] = useState({ code: '', name: '', address: '', owner: '' })
  const [floorForm, setFloorForm] = useState({ site_id: 0, name: '', level_no: 1, ownership: 'own', customer_name: '' })
  const [roomForm, setRoomForm] = useState({ floor_id: 0, name: '', is_rental: false, customer_name: '' })

  async function reload() {
    const [c, f, r, s] = await Promise.all([
      api<any[]>('/cost-centres'),
      api<any[]>('/floors'),
      api<any[]>('/rooms'),
      api<any[]>('/sites'),
    ])
    setCcs(c); setFloors(f); setRooms(r); setSites(s)
    setFloorForm((x) => ({ ...x, site_id: s[0]?.id || 0 }))
    setRoomForm((x) => ({ ...x, floor_id: f[0]?.id || 0 }))
  }
  useEffect(() => { reload().catch(console.error) }, [])

  async function createCc(e: FormEvent) {
    e.preventDefault()
    await api('/cost-centres', { method: 'POST', body: JSON.stringify(ccForm) })
    setCcForm({ code: '', name: '', address: '', owner: '' })
    await reload()
  }
  async function createFloor(e: FormEvent) {
    e.preventDefault()
    await api('/floors', { method: 'POST', body: JSON.stringify(floorForm) })
    await reload()
  }
  async function createRoom(e: FormEvent) {
    e.preventDefault()
    await api('/rooms', { method: 'POST', body: JSON.stringify(roomForm) })
    await reload()
  }

  return (
    <div>
      <h1>Cost Centres / Floors / Rooms</h1>
      <div className="two-col">
        <form className="card form-grid" onSubmit={createCc}>
          <h2>Create Cost Centre</h2>
          <label>Code <input value={ccForm.code} onChange={(e) => setCcForm({ ...ccForm, code: e.target.value })} required /></label>
          <label>Name <input value={ccForm.name} onChange={(e) => setCcForm({ ...ccForm, name: e.target.value })} required /></label>
          <label>Address <input value={ccForm.address} onChange={(e) => setCcForm({ ...ccForm, address: e.target.value })} /></label>
          <label>Owner <input value={ccForm.owner} onChange={(e) => setCcForm({ ...ccForm, owner: e.target.value })} /></label>
          <button type="submit">Create</button>
          <ul>{ccs.map((c) => <li key={c.id}>{c.code} — {c.name} — {c.address}</li>)}</ul>
        </form>
        <form className="card form-grid" onSubmit={createFloor}>
          <h2>Create Floor</h2>
          <label>Site
            <select value={floorForm.site_id} onChange={(e) => setFloorForm({ ...floorForm, site_id: Number(e.target.value) })}>
              {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </label>
          <label>Name <input value={floorForm.name} onChange={(e) => setFloorForm({ ...floorForm, name: e.target.value })} required /></label>
          <label>Level <input type="number" value={floorForm.level_no} onChange={(e) => setFloorForm({ ...floorForm, level_no: Number(e.target.value) })} /></label>
          <label>Ownership
            <select value={floorForm.ownership} onChange={(e) => setFloorForm({ ...floorForm, ownership: e.target.value })}>
              <option value="own">own</option>
              <option value="rental">rental customer</option>
            </select>
          </label>
          <label>Customer <input value={floorForm.customer_name} onChange={(e) => setFloorForm({ ...floorForm, customer_name: e.target.value })} /></label>
          <button type="submit">Create floor</button>
          <ul>{floors.map((f) => <li key={f.id}>{f.name} ({f.ownership} {f.customer_name})</li>)}</ul>
        </form>
      </div>
      <form className="card form-grid" onSubmit={createRoom}>
        <h2>Create Room</h2>
        <label>Floor
          <select value={roomForm.floor_id} onChange={(e) => setRoomForm({ ...roomForm, floor_id: Number(e.target.value) })}>
            {floors.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
          </select>
        </label>
        <label>Name <input value={roomForm.name} onChange={(e) => setRoomForm({ ...roomForm, name: e.target.value })} required /></label>
        <label>
          <input type="checkbox" checked={roomForm.is_rental} onChange={(e) => setRoomForm({ ...roomForm, is_rental: e.target.checked })} />
          Rental customer
        </label>
        <label>Customer <input value={roomForm.customer_name} onChange={(e) => setRoomForm({ ...roomForm, customer_name: e.target.value })} /></label>
        <button type="submit">Create room</button>
        <ul>{rooms.map((r) => <li key={r.id}>{r.name} — {r.is_rental ? `rental: ${r.customer_name}` : 'own'}</li>)}</ul>
      </form>
    </div>
  )
}
