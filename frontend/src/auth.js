const STORAGE_KEY = 'vectorrt_token'

export function getStoredToken() {
  try {
    return sessionStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

export function storeToken(token) {
  try {
    sessionStorage.setItem(STORAGE_KEY, token)
  } catch {
    // sessionStorage no disponible (privado, cookies bloqueadas...): la sesión no persiste al recargar.
  }
}

export function clearToken() {
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // no-op
  }
}

/** fetch autenticado; si el token ya no vale, lanza AuthExpiredError para que la app vuelva al login. */
export class AuthExpiredError extends Error {}

export async function authFetch(token, input, init = {}) {
  const res = await fetch(input, {
    ...init,
    headers: { ...(init.headers || {}), Authorization: `Bearer ${token}` },
  })
  if (res.status === 401) {
    throw new AuthExpiredError('Sesión caducada')
  }
  return res
}
