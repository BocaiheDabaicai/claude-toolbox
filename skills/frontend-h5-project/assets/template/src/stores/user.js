import { defineStore } from 'pinia'
import { getToken, removeToken, removeUserId, setToken, setUserId } from '@/utils/auth'

// TODO: 接入目标后端后，替换 login / getInfo / logout 的实现。
// 约定：
// - token 持久化到 localStorage；
// - userInfo 只在内存，刷新后由路由守卫调用 getInfo() 恢复；
// - 当前用户 ID 写入 auth.getUserId()，供需要会员归属的接口读取。
export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken(),
    userInfo: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    async login(data) {
      // 示例：
      // const res = await loginApi(data)
      // this.token = res.data.token
      // setToken(this.token)
      // await this.getInfo()
      throw new Error('登录接口未接入，请实现 stores/user.js 的 login')
    },
    async getInfo() {
      // 示例：
      // const res = await getUserInfo()
      // this.userInfo = res.data.userInfo
      // setUserId(this.userInfo?.id)
      // return this.userInfo
      if (import.meta.env.DEV && this.token.startsWith('demo-')) {
        this.userInfo = this.userInfo || { id: 1, name: '演示用户' }
        return this.userInfo
      }
      throw new Error('用户信息接口未接入，请实现 stores/user.js 的 getInfo')
    },
    async logout() {
      this.reset()
    },
    // 仅用于模板预览：真实项目接入登录接口后删除
    loginDemo() {
      const token = `demo-${Date.now()}`
      this.token = token
      this.userInfo = { id: 1, name: '演示用户' }
      setToken(token)
      setUserId(1)
    },
    reset() {
      this.token = ''
      this.userInfo = null
      removeToken()
      removeUserId()
    },
  },
})
