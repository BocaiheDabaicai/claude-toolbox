<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import BottomNav from '@/components/BottomNav.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import ToastHost from '@/components/ToastHost.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 首屏守卫拉取用户信息期间用目标路由渲染底栏，避免刷新时底栏短时消失
const bootTarget = router.resolve(window.location.hash.slice(1) || '/')
const booting = computed(() => router.currentRoute.value.matched.length === 0)
const currentRoute = computed(() => (booting.value ? bootTarget : router.currentRoute.value))
const showBottomNav = computed(
  () => userStore.isLoggedIn && currentRoute.value.name !== 'login' && !currentRoute.value.meta.hideBottomNav,
)
const navActiveName = computed(() => (booting.value ? bootTarget.name : ''))

// 购物车角标等跨页数量：从对应 store 派生后传给 BottomNav
// const navBadges = computed(() => ({ cart: cartStore.badge }))
</script>

<template>
  <router-view v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </router-view>

  <BottomNav v-if="showBottomNav" :active-name="navActiveName" />

  <ToastHost />
  <ConfirmDialog />
</template>
