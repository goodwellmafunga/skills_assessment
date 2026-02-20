import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api/client'

export default function Signup() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/auth/signup', form)
      localStorage.setItem('access_token', res.data.access_token)
      nav('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Signup failed')
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-100 to-white">
      <div className="card p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-1">Create account</h2>
        <p className="text-slate-500 mb-6">Get started with admin dashboard access.</p>

        <form onSubmit={submit} className="space-y-3">
          <input className="w-full border rounded-xl px-3 py-2" placeholder="Full name" value={form.full_name} onChange={(e)=>setForm({...form,full_name:e.target.value})}/>
          <input className="w-full border rounded-xl px-3 py-2" placeholder="Email" type="email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})}/>
          <input className="w-full border rounded-xl px-3 py-2" placeholder="Password" type="password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})}/>
          <button className="w-full bg-slate-900 text-white rounded-xl py-2">Sign up</button>
        </form>

        {error && <div className="mt-4 text-sm text-red-600">{error}</div>}
        <p className="text-sm mt-4">Have an account? <Link className="underline" to="/login">Login</Link></p>
      </div>
    </div>
  )
}
