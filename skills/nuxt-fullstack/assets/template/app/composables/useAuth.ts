import { storeToRefs } from 'pinia'
import { useAuthStore } from '~/stores/auth'

/**
 * 兼容层：页面继续使用 useAuth()，底层登录态统一由 Pinia 管理。
 * 返回 ref 以保持原有 user.value / initialized.value 用法。
 */
export function useAuth() {
  const store = useAuthStore()
  const { user, initialized, loading } = storeToRefs(store)

  function fetchUser(force = false) {
    return store.fetchUser(force)
  }

  function login(email: string, password: string) {
    return store.login(email, password)
  }

  function logout() {
    return store.logout()
  }

  return { user, initialized, loading, fetchUser, login, logout }
}
