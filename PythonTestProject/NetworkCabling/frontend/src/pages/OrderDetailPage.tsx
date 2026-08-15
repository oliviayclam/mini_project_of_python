import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api'

type Order = {
  id: number
  request_no: string
  status: string
  remarks: string
  approver_comment: string
  lines: Array<{
    id: number
    line_no: number
    path_group: string
    path_index: number
    endpoint_a: string
    endpoint_b: string
    requested_length_m: number
    routing_notes: string
    cable_type_id?: number
    service_type_id?: number
  }>
}

export default function OrderDetailPage() {
  const { id } = useParams()
  const [order, setOrder] = useState<Order | null>(null)
  useEffect(() => {
    api<Order>(`/orders/${id}`).then(setOrder).catch(console.error)
  }, [id])
  if (!order) return <p>Loading…</p>
  return (
    <div>
      <h1>{order.request_no}</h1>
      <p>Status: <strong>{order.status}</strong></p>
      <p>Remarks: {order.remarks || '-'}</p>
      <p>Approver comment: {order.approver_comment || '-'}</p>
      <h2>Full paths</h2>
      <table>
        <thead>
          <tr>
            <th>#</th><th>Group</th><th>From</th><th>To</th><th>Length</th><th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {order.lines.map((l) => (
            <tr key={l.id}>
              <td>{l.line_no}</td>
              <td>{l.path_group}-{l.path_index}</td>
              <td>{l.endpoint_a}</td>
              <td>{l.endpoint_b}</td>
              <td>{l.requested_length_m} m</td>
              <td>{l.routing_notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
