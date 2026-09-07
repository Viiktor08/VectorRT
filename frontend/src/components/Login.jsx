import { useState } from 'react'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const body = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(body.detail || 'No se pudo iniciar sesión')
      }
      onLogin(body.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-sm flex-col gap-4 rounded-md border border-gray-800 bg-gray-950 p-6"
      >
        <div>
          <h1 className="text-xl font-semibold text-white">VectorRT</h1>
          <p className="text-sm text-gray-400">Inicia sesión para acceder al laboratorio.</p>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="username" className="text-sm text-gray-400">
            Usuario
          </label>
          <input
            id="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-white"
            autoComplete="username"
            required
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="password" className="text-sm text-gray-400">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-white"
            autoComplete="current-password"
            required
          />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-purple-600 px-4 py-2 font-medium text-white
                     hover:bg-purple-500 disabled:bg-gray-800 disabled:text-gray-500"
        >
          {loading ? 'Entrando…' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
