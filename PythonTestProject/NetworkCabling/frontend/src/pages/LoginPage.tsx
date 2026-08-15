import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, login } from '../api'
import type { User } from '../api'

export default function LoginPage({ onLogin }: { onLogin: (u: User) => void }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const nav = useNavigate()

  async function submit(e: FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      const me = await api<User>('/auth/me')
      onLogin(me)
      nav('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login-card" onSubmit={submit}>
        <h1>Network Cabling</h1>
        <p className="muted">Demo: admin/admin123 · operator/operator123 · vendor/vendor123</p>
        {error && <p className="error">{error}</p>}
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit">Sign in</button>
      </form>
    </div>
  )
}
