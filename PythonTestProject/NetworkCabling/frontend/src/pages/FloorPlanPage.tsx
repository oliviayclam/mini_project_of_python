import { useEffect, useRef, useState } from 'react'
import { api } from '../api'

type Floor = { id: number; name: string }
type Plan = {
  id: number
  floor_id: number
  scale_m_per_px: number
  canvas_data: string
  segments: Array<{ id: number; start_x: number; start_y: number; end_x: number; end_y: number; path_length_m: number }>
}

export default function FloorPlanPage() {
  const [floors, setFloors] = useState<Floor[]>([])
  const [floorId, setFloorId] = useState(0)
  const [plan, setPlan] = useState<Plan | null>(null)
  const [estimate, setEstimate] = useState<number | null>(null)
  const start = useRef<{ x: number; y: number } | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    api<Floor[]>('/floors').then((f) => {
      setFloors(f)
      if (f[0]) setFloorId(f[0].id)
    })
  }, [])

  useEffect(() => {
    if (!floorId) return
    api<Plan>(`/floors/${floorId}/plan`).then(setPlan)
  }, [floorId])

  useEffect(() => {
    const c = canvasRef.current
    if (!c || !plan) return
    const ctx = c.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, c.width, c.height)
    ctx.fillStyle = '#f8fafc'
    ctx.fillRect(0, 0, c.width, c.height)
    ctx.strokeStyle = '#cbd5e1'
    for (let i = 0; i < c.width; i += 40) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, c.height); ctx.stroke()
    }
    for (let j = 0; j < c.height; j += 40) {
      ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(c.width, j); ctx.stroke()
    }
    ctx.strokeStyle = '#1d4ed8'
    ctx.lineWidth = 3
    plan.segments.forEach((s) => {
      ctx.beginPath()
      ctx.moveTo(s.start_x, s.start_y)
      ctx.lineTo(s.end_x, s.end_y)
      ctx.stroke()
    })
  }, [plan])

  async function onClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    if (!start.current) {
      start.current = { x, y }
      return
    }
    await api(`/floors/${floorId}/plan/segments`, {
      method: 'POST',
      body: JSON.stringify({
        start_x: start.current.x,
        start_y: start.current.y,
        end_x: x,
        end_y: y,
        notes: 'drawn path',
      }),
    })
    start.current = null
    setPlan(await api(`/floors/${floorId}/plan`))
  }

  async function calc() {
    const data = await api<{ estimated_length_m: number }>(`/floors/${floorId}/plan/estimate-path-length`, {
      method: 'POST',
    })
    setEstimate(data.estimated_length_m)
  }

  return (
    <div>
      <h1>Floor Plan Designer</h1>
      <p className="muted">Click twice to draw a path segment. Used for new customer move-in path length.</p>
      <div className="row-between">
        <select value={floorId} onChange={(e) => setFloorId(Number(e.target.value))}>
          {floors.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
        </select>
        <button type="button" onClick={calc}>Estimate total path length</button>
      </div>
      {estimate !== null && <p className="ok">Estimated length: {estimate} m</p>}
      <canvas ref={canvasRef} width={800} height={480} className="floor-canvas" onClick={onClick} />
      <ul>
        {(plan?.segments || []).map((s) => (
          <li key={s.id}>Segment #{s.id}: {s.path_length_m} m</li>
        ))}
      </ul>
    </div>
  )
}
