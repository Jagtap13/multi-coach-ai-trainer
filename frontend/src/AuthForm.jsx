import { useState, useEffect, useRef } from 'react'

const API_URL = 'http://127.0.0.1:8000'

// Read from frontend/.env (VITE_GOOGLE_CLIENT_ID=...). Must match the
// GOOGLE_CLIENT_ID environment variable the backend checks against -
// same Client ID from Google Cloud Console -> Clients -> Web application.
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

function AuthForm({ onAuthSuccess }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Forgot/reset password state
  const [resetToken, setResetToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [infoMessage, setInfoMessage] = useState('')

  const googleButtonRef = useRef(null)

  // If the user arrived here via the emailed reset link
  // (http://localhost:5173/?reset_token=...), drop straight into the
  // reset-password form with the token pre-filled.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const tokenFromUrl = params.get('reset_token')
    if (tokenFromUrl) {
      setResetToken(tokenFromUrl)
      setMode('reset')
      // Clean the token out of the URL so it isn't left sitting in
      // browser history or visible on refresh/share.
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  // Loads Google's Identity Services script once, then renders the
  // "Sign in with Google" button into googleButtonRef whenever we're
  // on the login or register screen.
  useEffect(() => {
    if (mode !== 'login' && mode !== 'register') return

    const initializeGoogleButton = () => {
      if (!window.google || !googleButtonRef.current) return
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCredential,
      })
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        width: 320,
        text: mode === 'login' ? 'signin_with' : 'signup_with',
      })
    }

    if (window.google) {
      initializeGoogleButton()
      return
    }

    const existingScript = document.getElementById('google-identity-script')
    if (existingScript) {
      existingScript.addEventListener('load', initializeGoogleButton)
      return () => existingScript.removeEventListener('load', initializeGoogleButton)
    }

    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.id = 'google-identity-script'
    script.async = true
    script.onload = initializeGoogleButton
    document.body.appendChild(script)
  }, [mode])

  const handleGoogleCredential = async (response) => {
    resetFeedback()
    setLoading(true)
    try {
      const apiResponse = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential }),
      })

      const data = await apiResponse.json()

      if (!apiResponse.ok) {
        throw new Error(data.detail || 'Google sign-in failed')
      }

      onAuthSuccess(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const resetFeedback = () => {
    setError('')
    setInfoMessage('')
  }

  const switchMode = (nextMode) => {
    setMode(nextMode)
    resetFeedback()
  }

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

  const handleForgotPassword = async (e) => {
    e.preventDefault()
    resetFeedback()
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong')
      }

      setInfoMessage(data.message)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e) => {
    e.preventDefault()
    resetFeedback()

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: resetToken, new_password: newPassword }),
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
      <div className="w-full max-w-sm bg-(--color-bg-elevated) rounded-md p-8 border border-(--color-border)">
        <h1 className="font-[Oswald] uppercase tracking-wide text-2xl font-semibold mb-1">
          AI Personal Trainer
        </h1>
        <p className="text-(--color-chalk-dim) text-sm mb-6">
          {mode === 'login' && 'Log in to continue'}
          {mode === 'register' && 'Create your account'}
          {mode === 'forgot' && 'Reset your password'}
          {mode === 'reset' && 'Choose a new password'}
        </p>

        {(mode === 'login' || mode === 'register') && (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-xs text-(--color-chalk-dim) block mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-(--color-input-bg) rounded-md px-3 py-2 text-sm outline-none"
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
                className="w-full bg-(--color-input-bg) rounded-md px-3 py-2 text-sm outline-none"
              />
            </div>

            {mode === 'login' && (
              <button
                type="button"
                onClick={() => switchMode('forgot')}
                className="text-xs text-(--color-chalk-dim) hover:text-(--color-chalk) text-left -mt-2 underline w-fit"
              >
                Forgot password?
              </button>
            )}

            {error && (
              <p className="text-xs text-(--color-error-text) bg-(--color-error-bg) rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="rounded-md py-2 text-sm font-medium uppercase tracking-wide disabled:opacity-50 mt-2"
              style={{ backgroundColor: 'var(--color-chalk)', color: 'var(--color-bg)' }}
            >
              {loading ? 'Please wait...' : mode === 'login' ? 'Log In' : 'Register'}
            </button>
          </form>
        )}

        {(mode === 'login' || mode === 'register') && (
          <>
            <div className="flex items-center gap-3 my-4">
              <div className="flex-1 h-px bg-(--color-border)" />
              <span className="text-[10px] uppercase tracking-widest text-(--color-chalk-dim)">or</span>
              <div className="flex-1 h-px bg-(--color-border)" />
            </div>
            <div ref={googleButtonRef} className="flex justify-center" />
          </>
        )}

        {mode === 'forgot' && (
          <form onSubmit={handleForgotPassword} className="flex flex-col gap-4">
            <div>
              <label className="text-xs text-(--color-chalk-dim) block mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-(--color-input-bg) rounded-md px-3 py-2 text-sm outline-none"
              />
            </div>

            {infoMessage && (
              <p className="text-xs text-(--color-chalk-dim) bg-(--color-input-bg) rounded-md px-3 py-2">
                {infoMessage}
              </p>
            )}

            {error && (
              <p className="text-xs text-(--color-error-text) bg-(--color-error-bg) rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="rounded-md py-2 text-sm font-medium uppercase tracking-wide disabled:opacity-50 mt-2"
              style={{ backgroundColor: 'var(--color-chalk)', color: 'var(--color-bg)' }}
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        )}

        {mode === 'reset' && (
          <form onSubmit={handleResetPassword} className="flex flex-col gap-4">
            <p className="text-xs text-(--color-chalk-dim)">
              Enter a new password for your account.
            </p>

            <div>
              <label className="text-xs text-(--color-chalk-dim) block mb-1">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
                autoFocus
                className="w-full bg-(--color-input-bg) rounded-md px-3 py-2 text-sm outline-none"
              />
            </div>

            <div>
              <label className="text-xs text-(--color-chalk-dim) block mb-1">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                className="w-full bg-(--color-input-bg) rounded-md px-3 py-2 text-sm outline-none"
              />
            </div>

            {error && (
              <p className="text-xs text-(--color-error-text) bg-(--color-error-bg) rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="rounded-md py-2 text-sm font-medium uppercase tracking-wide disabled:opacity-50 mt-2"
              style={{ backgroundColor: 'var(--color-chalk)', color: 'var(--color-bg)' }}
            >
              {loading ? 'Please wait...' : 'Reset Password'}
            </button>
          </form>
        )}

        <button
          onClick={() => switchMode(mode === 'login' || mode === 'forgot' || mode === 'reset' ? 'register' : 'login')}
          className="text-xs text-(--color-chalk-dim) mt-4 underline"
        >
          {(mode === 'login' || mode === 'forgot' || mode === 'reset')
            ? "Don't have an account? Register"
            : 'Already have an account? Log in'}
        </button>

        {(mode === 'forgot' || mode === 'reset') && (
          <button
            onClick={() => switchMode('login')}
            className="text-xs text-(--color-chalk-dim) mt-2 underline block"
          >
            Back to log in
          </button>
        )}
      </div>
    </div>
  )
}

export default AuthForm