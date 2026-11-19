import { createRouter, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

router.beforeEach(async (to) => {
  // 如果后端要求登录接口携带非 0 的店铺/商户标识，在这里先初始化：
  // const configStore = useConfigStore()
  // if (!configStore.hasStore) await configStore.ensureInitialized().catch(() => {})

  const userStore = useUserStore()
  if (!userStore.isLoggedIn) {
    if (to.name === 'login') return true
    return { name: 'login', query: to.fullPath === '/' ? {} : { redirect: to.fullPath } }
  }

  // 刷新后内存态丢失，用 token 重新拉取用户信息
  if (!userStore.userInfo) {
    try {
      await userStore.getInfo()
    } catch {
      userStore.reset()
      return { name: 'login' }
    }
  }

  if (to.name === 'login') return { name: 'home' }
})

export default router
