export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path.startsWith('/api/')) return

  const { user, fetchUser } = useAuth()
  await fetchUser()

  const isLogin = to.path === '/login'
  if (!user.value && !isLogin) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
  if (user.value && isLogin) {
    return navigateTo('/')
  }
})
