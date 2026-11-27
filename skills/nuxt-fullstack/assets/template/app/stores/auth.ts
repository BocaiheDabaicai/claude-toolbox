import { defineStore } from 'pinia'
import type { ApiResponse } from '~~/shared/types/api'
import type { SessionUser } from '~~/shared/types/auth'

interface AuthState {
  user: SessionUser | null
  initialized: boolean
  loading: boolean
}

/**
 * 登录态是全局共享状态，统一放 Pinia（与 frontend-h5-project 的 Pinia 约定一致）。
 * 页面级数据仍走 useApiFetch，不放进 store。
 */
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    initialized: false,
    loading: false,
  }),

  actions: {
    async fetchUser(force = false) {
      if (this.initialized && !force) return this.user

      this.loading = true
      try {
        const requestFetch = import.meta.server ? useRequestFetch() : $fetch
        const response = await requestFetch<ApiResponse<{ user: SessionUser }>>(
          '/api/auth/me',
        )
        this.user = response.data.user
      } catch {
        this.user = null
      } finally {
        this.initialized = true
        this.loading = false
      }
      return this.user
    },

    async login(email: string, password: string) {
      const response = await $fetch<ApiResponse<{ user: SessionUser }>>(
        '/api/auth/login',
        {
          method: 'POST',
          body: { email, password },
        },
      )
      this.user = response.data.user
      this.initialized = true
      return this.user
    },

    async logout() {
      await $fetch('/api/auth/logout', { method: 'POST' }).catch(() => {})
      this.user = null
      this.initialized = true
      await navigateTo('/login')
    },
  },
})
