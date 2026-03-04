import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  email: string
  username: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(
    JSON.parse(localStorage.getItem('user') || 'null')
  )

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(newToken: string, newUser: User) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function authHeaders(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token.value) h['Authorization'] = `Bearer ${token.value}`
    return h
  }

  async function validateSession() {
    // If local user exists without token, clean stale state.
    if (!token.value && user.value) {
      logout()
      return false
    }
    if (!token.value) return false

    try {
      const res = await fetch('/api/auth/me', {
        headers: authHeaders(),
      })
      if (!res.ok) {
        logout()
        return false
      }
      return true
    } catch {
      // Network issue: keep token for now, avoid accidental logout.
      return true
    }
  }

  return { token, user, isLoggedIn, setAuth, logout, authHeaders, validateSession }
})
