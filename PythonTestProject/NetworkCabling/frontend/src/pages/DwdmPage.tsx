import { useEffect, useState } from 'react'
import { api } from '../api'

export default function DwdmPage() {
  const [systems, setSystems] = useState<any[]>([])
  const [links, setLinks] = useState<any[]>([])
  const [channels, setChannels] = useState<any[]>([])
  useEffect(() => {
    Promise.all([api('/dwdm/systems'), api('/dwdm/links'), api('/dwdm/channels')]).then(
      ([s, l, c]) => {
        setSystems(s as any[]); setLinks(l as any[]); setChannels(c as any[])
      },
    )
  }, [])
  return (
    <div>
      <h1>DWDM (optional extension)</h1>
      <div className="two-col">
        <div className="card">
          <h2>Systems</h2>
          <ul>{systems.map((s) => <li key={s.id}>{s.name} — {s.description}</li>)}</ul>
        </div>
        <div className="card">
          <h2>Links</h2>
          <ul>{links.map((l) => <li key={l.id}>{l.name} ({l.distance_km} km)</li>)}</ul>
        </div>
      </div>
      <div className="card">
        <h2>Optical channels</h2>
        <table>
          <thead><tr><th>ITU</th><th>Wavelength</th><th>Service</th><th>Status</th><th>Port</th></tr></thead>
          <tbody>
            {channels.map((c) => (
              <tr key={c.id}>
                <td>{c.itu_channel}</td>
                <td>{c.wavelength_nm}</td>
                <td>{c.client_service}</td>
                <td>{c.status}</td>
                <td>{c.port_id || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
