import type { ApiResponse } from '~~/shared/types/api'
import type { SessionUser } from '~~/shared/types/auth'

export function useAuth() {
  const user = useState<SessionUser | null>('auth.user', () => null)
  const initialized = useState<boolean>('auth.initialized', () => false)
  const loading = useState<boolean>('auth.loading', () => false)

  async function fetchUser(force = false) {
    if (initialized.value && !force) return user.value

    loading.value = true
    try {
      const requestFetch = import.meta.server ? useRequestFetch() : $fetch
      const response = await requestFetch<ApiResponse<{ user: SessionUser }>>(
        '/api/auth/me',
      )
      user.value = response.data.user
    } catch {
      user.value = null
    } finally {
      initialized.value = true
      loading.value = false
    }
    return user.value
  }

  async function login(email: string, password: string) {
    const response = await $fetch<ApiResponse<{ user: SessionUser }>>(
      '/api/auth/login',
      {
        method: 'POST',
        body: { email, password },
      },
    )
    user.value = response.data.user
    initialized.value = true
    return user.value
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' }).catch(() => {})
    user.value = null
    initialized.value = true
    await navigateTo('/login')
  }

  return { user, initialized, loading, fetchUser, login, logout }
}
