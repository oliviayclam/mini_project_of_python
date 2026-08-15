import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

type Rack = {
  id: number
  name: string
  manufacturer: string
  model: string
  u_height: number
  install_date?: string
  expire_date?: string
  asset_tag: string
}

export default function RacksPage() {
  const [racks, setRacks] = useState<Rack[]>([])
  useEffect(() => {
    api<Rack[]>('/racks').then(setRacks).catch(console.error)
  }, [])
  return (
    <div>
      <h1>Racks / ODF</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Manufacturer</th><th>Model</th><th>U</th><th>Install</th><th>Expire</th><th>Tag</th><th></th>
          </tr>
        </thead>
        <tbody>
          {racks.map((r) => (
            <tr key={r.id}>
              <td>{r.name}</td>
              <td>{r.manufacturer}</td>
              <td>{r.model}</td>
              <td>{r.u_height}</td>
              <td>{r.install_date || '-'}</td>
              <td>{r.expire_date || '-'}</td>
              <td>{r.asset_tag}</td>
              <td><Link to={`/racks/${r.id}`}>2D View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
