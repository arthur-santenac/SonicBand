import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { apiFetch } from '@/services/api'

const TOKEN_KEY = 'sonicband_token'

function readToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

function writeToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // stockage indisponible (navigation privée…) : la session reste en mémoire
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(readToken())
  const user = ref(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function setSession(data) {
    token.value = data.access_token
    user.value = data.utilisateur
    writeToken(data.access_token)
  }

  async function register(nom, email, motDePasse) {
    const data = await apiFetch('/api/auth/register', {
      method: 'POST',
      body: { nom, email, mot_de_passe: motDePasse },
    })
    setSession(data)
  }

  async function login(email, motDePasse) {
    const data = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: { email, mot_de_passe: motDePasse },
    })
    setSession(data)
  }

  // Recharge l'utilisateur à partir du jeton stocké ; déconnecte si le jeton est invalide.
  async function fetchMe() {
    if (!token.value) return null
    try {
      user.value = await apiFetch('/api/auth/me', { token: token.value })
    } catch (err) {
      if (err.status === 401) logout()
      else throw err
    }
    return user.value
  }

  function logout() {
    token.value = null
    user.value = null
    writeToken(null)
  }

  return { token, user, isAuthenticated, register, login, fetchMe, logout }
})
