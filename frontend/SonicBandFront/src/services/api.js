const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

function extractMessage(data, status) {
  const detail = data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const field = detail[0]?.loc?.at(-1)
    if (field === 'email') return 'Adresse e-mail invalide.'
    if (field === 'mot_de_passe') return 'Le mot de passe doit contenir au moins 8 caractères.'
    if (field === 'nom') return 'Le nom affiché est obligatoire.'
    return 'Données invalides.'
  }
  return `Erreur serveur (${status}).`
}

export async function apiFetch(path, { method = 'GET', body, token } = {}) {
  const options = { method, headers: { Accept: 'application/json' } }
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }
  if (token) options.headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, options)
  } catch {
    throw new ApiError('Impossible de joindre le serveur. Le backend est-il lancé ?', 0)
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(extractMessage(data, response.status), response.status)
  return data
}
