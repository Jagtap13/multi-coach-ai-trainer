import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong')
      }

      onAuthSuccess(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm bg-(--color-bg-elevated) rounded-md p-8 border border-white/10">
        <h1 className="font-[Oswald] uppercase tracking-wide text-2xl font-semibold mb-1">
          AI Personal Trainer
        </h1>
        <p className="text-(--color-chalk-dim) text-sm mb-6">
          {mode === 'login' ? 'Log in to continue' : 'Create your account'}
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="text-xs text-(--color-chalk-dim) block mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-black/20 rounded-md px-3 py-2 text-sm outline-none"
            />
          </div>

          <div>
            <label className="text-xs text-(--color-chalk-dim) block mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full bg-black/20 rounded-md px-3 py-2 text-sm outline-none"
            />
          </div>

          {error && (
            <p className="text-xs text-red-400 bg-red-900/20 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="bg-white text-black rounded-md py-2 text-sm font-medium uppercase tracking-wide disabled:opacity-50 mt-2"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Log In' : 'Register'}
          </button>
        </form>

        <button
          onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
          className="text-xs text-(--color-chalk-dim) mt-4 underline"
        >
          {mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Log in'}
        </button>
      </div>
    </div>
  )
}

export default AuthForm