import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function SearchPage() {
  const [filters, setFilters] = useState({
    cost_centre_id: '',
    floor_id: '',
    room_id: '',
    rack_id: '',
    panel_id: '',
    port_remark: '',
    cable_type_id: '',
    service_type_id: '',
    view_mode: '2d',
  })
  const [result, setResult] = useState<any>(null)
  const [masters, setMasters] = useState<any>({})

  useEffect(() => {
    Promise.all([
      api('/cost-centres'),
      api('/floors'),
      api('/rooms'),
      api('/racks'),
      api('/panels'),
      api('/cable-types'),
      api('/service-types'),
    ]).then(([cc, floors, rooms, racks, panels, cts, sts]) => {
      setMasters({ cc, floors, rooms, racks, panels, cts, sts })
    })
  }, [])

  async function search() {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.set(k, String(v))
    })
    setResult(await api(`/search/assets?${params}`))
  }

  return (
    <div>
      <h1>Search</h1>
      <div className="card form-grid">
        <label>
          Cost centre
          <select value={filters.cost_centre_id} onChange={(e) => setFilters({ ...filters, cost_centre_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.cc || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Floor
          <select value={filters.floor_id} onChange={(e) => setFilters({ ...filters, floor_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.floors || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Room
          <select value={filters.room_id} onChange={(e) => setFilters({ ...filters, room_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.rooms || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Rack
          <select value={filters.rack_id} onChange={(e) => setFilters({ ...filters, rack_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.racks || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Panel
          <select value={filters.panel_id} onChange={(e) => setFilters({ ...filters, panel_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.panels || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Port remark
          <input value={filters.port_remark} onChange={(e) => setFilters({ ...filters, port_remark: e.target.value })} />
        </label>
        <label>
          Cable type
          <select value={filters.cable_type_id} onChange={(e) => setFilters({ ...filters, cable_type_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.cts || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          Service type
          <select value={filters.service_type_id} onChange={(e) => setFilters({ ...filters, service_type_id: e.target.value })}>
            <option value="">Any</option>
            {(masters.sts || []).map((x: any) => <option key={x.id} value={x.id}>{x.name}</option>)}
          </select>
        </label>
        <label>
          View
          <select value={filters.view_mode} onChange={(e) => setFilters({ ...filters, view_mode: e.target.value })}>
            <option value="2d">2D first</option>
            <option value="3d">3D</option>
          </select>
        </label>
        <button type="button" onClick={search}>Search</button>
      </div>

      {result && (
        <div className="card">
          <h2>Results ({result.view_mode})</h2>
          <h3>Racks</h3>
          <ul>
            {result.racks.map((r: any) => (
              <li key={r.id}>
                <Link to={`/racks/${r.id}`}>{r.name}</Link> — {r.floor}/{r.room} — {r.manufacturer} {r.model}
              </li>
            ))}
          </ul>
          <h3>Ports</h3>
          <ul>
            {result.ports.map((p: any) => (
              <li key={p.id}>
                <span className="swatch" style={{ background: p.color }} />
                {p.name} — {p.status} — {p.remark || '-'}
              </li>
            ))}
          </ul>
          <h3>Cables</h3>
          <ul>
            {result.cables.map((c: any) => (
              <li key={c.id}>{c.label || c.id}: {c.cable_type} / {c.service_type} / {c.length_m}m</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
