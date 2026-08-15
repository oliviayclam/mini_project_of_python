import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api'

type Port = {
  id: number
  name: string
  port_number: number
  panel_id?: number
  status_id?: number
  remark: string
  connector_type: string
}
type Status = { id: number; name: string; color_hex: string }
type Panel = { id: number; name: string; rack_id: number; u_position: number; port_count: number }
type Cable = {
  id: number
  label: string
  length_m: number
  a_port_id?: number
  b_port_id?: number
  b_customer_name: string
  cable_type_id: number
}
type CableType = { id: number; name: string }
type Rack = { id: number; name: string; u_height: number; manufacturer: string; model: string }

export default function Rack2DPage() {
  const { id } = useParams()
  const rackId = Number(id)
  const [rack, setRack] = useState<Rack | null>(null)
  const [panels, setPanels] = useState<Panel[]>([])
  const [ports, setPorts] = useState<Port[]>([])
  const [statuses, setStatuses] = useState<Status[]>([])
  const [cables, setCables] = useState<Cable[]>([])
  const [types, setTypes] = useState<CableType[]>([])
  const [selected, setSelected] = useState<Port | null>(null)
  const [mode3d, setMode3d] = useState(false)

  useEffect(() => {
    Promise.all([
      api<Rack>(`/racks/${rackId}`),
      api<Panel[]>('/panels'),
      api<Port[]>(`/ports?rack_id=${rackId}`),
      api<Status[]>('/port-statuses'),
      api<Cable[]>('/cables'),
      api<CableType[]>('/cable-types'),
    ]).then(([r, p, po, s, c, t]) => {
      setRack(r)
      setPanels(p.filter((x) => x.rack_id === rackId))
      setPorts(po)
      setStatuses(s)
      setCables(c)
      setTypes(t)
    })
  }, [rackId])

  const statusMap = useMemo(() => Object.fromEntries(statuses.map((s) => [s.id, s])), [statuses])
  const typeMap = useMemo(() => Object.fromEntries(types.map((t) => [t.id, t.name])), [types])
  const cableForPort = selected
    ? cables.find((c) => c.a_port_id === selected.id || c.b_port_id === selected.id)
    : undefined

  if (!rack) return <p>Loading…</p>

  return (
    <div className="rack-layout">
      <div>
        <div className="row-between">
          <h1>{rack.name} — {mode3d ? '3D' : '2D'} view</h1>
          <button type="button" className="secondary" onClick={() => setMode3d((v) => !v)}>
            Switch to {mode3d ? '2D' : '3D'}
          </button>
        </div>
        <p className="muted">{rack.manufacturer} {rack.model} · {rack.u_height}U</p>
        {mode3d ? (
          <div className="rack-3d">
            <div className="rack-3d-box">
              <p>Basic 3D placeholder (orbit view in phase 2).</p>
              <p>Showing same ports as 2D.</p>
            </div>
          </div>
        ) : (
          <div className="rack-2d">
            {Array.from({ length: rack.u_height }, (_, i) => rack.u_height - i).map((u) => {
              const panel = panels.find((p) => p.u_position === u)
              return (
                <div key={u} className="u-row">
                  <span className="u-label">U{u}</span>
                  <div className="u-slot">
                    {panel ? (
                      <div className="panel-block">
                        <strong>{panel.name}</strong>
                        <div className="ports">
                          {ports
                            .filter((p) => p.panel_id === panel.id)
                            .map((p) => {
                              const st = p.status_id ? statusMap[p.status_id] : undefined
                              return (
                                <button
                                  key={p.id}
                                  type="button"
                                  className="port-dot"
                                  style={{ background: st?.color_hex || '#64748b' }}
                                  title={`${p.name} ${st?.name || ''}`}
                                  onClick={() => setSelected(p)}
                                >
                                  {p.port_number}
                                </button>
                              )
                            })}
                        </div>
                      </div>
                    ) : (
                      <span className="empty-u">empty</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
      <aside className="side-panel card">
        <h2>Port details</h2>
        {!selected && <p className="muted">Click a port</p>}
        {selected && (
          <>
            <p><strong>{selected.name}</strong></p>
            <p>Status: {selected.status_id ? statusMap[selected.status_id]?.name : '-'}</p>
            <p>Connector: {selected.connector_type}</p>
            <p>Remark: {selected.remark || '-'}</p>
            {cableForPort ? (
              <>
                <hr />
                <p>Cable: {cableForPort.label || `#${cableForPort.id}`}</p>
                <p>Type: {typeMap[cableForPort.cable_type_id] || '-'}</p>
                <p>Length: {cableForPort.length_m} m</p>
                <p>Far end: {cableForPort.b_customer_name || cableForPort.b_port_id || '-'}</p>
              </>
            ) : (
              <p className="muted">No cable on this port</p>
            )}
          </>
        )}
      </aside>
    </div>
  )
}
