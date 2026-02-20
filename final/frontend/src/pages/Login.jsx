import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api/client'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '', code: '', temp_token: '' })
  const [need2FA, setNeed2FA] = useState(false)
  const [error, setError] = useState('')
  const nav = useNavigate()

  const login = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/auth/login', { email: form.email, password: form.password })
      if (res.data.mfa_required) {
        setNeed2FA(true)
        setForm({ ...form, temp_token: res.data.temp_token })
      } else {
        localStorage.setItem('access_token', res.data.access_token)
        nav('/dashboard')
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    }
  }

  const verify2fa = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/auth/2fa/verify-login', {
        temp_token: form.temp_token,
        code: form.code,
      })
      localStorage.setItem('access_token', res.data.access_token)
      nav('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || '2FA verification failed')
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-100 to-white">
      <div className="card p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-1">Welcome back</h2>
        <p className="text-slate-500 mb-6">Sign in to the admin dashboard.</p>

        {!need2FA ? (
          <form onSubmit={login} className="space-y-3">
            <input className="w-full border rounded-xl px-3 py-2" placeholder="Email" type="email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})}/>
            <input className="w-full border rounded-xl px-3 py-2" placeholder="Password" type="password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})}/>
            <button className="w-full bg-slate-900 text-white rounded-xl py-2">Login</button>
          </form>
        ) : (
          <form onSubmit={verify2fa} className="space-y-3">
            <input className="w-full border rounded-xl px-3 py-2" placeholder="Authenticator code" value={form.code} onChange={(e)=>setForm({...form,code:e.target.value})}/>
            <button className="w-full bg-slate-900 text-white rounded-xl py-2">Verify 2FA</button>
          </form>
        )}

        {error && <div className="mt-4 text-sm text-red-600">{error}</div>}
        <p className="text-sm mt-4">No account? <Link className="underline" to="/signup">Create one</Link></p>
      </div>
    </div>
  )
}
