<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarOpen = ref(false)

const nav = [
  { name: 'admin-home', to: '/admin', label: '仪表盘', desc: '业务总览' },
  { name: 'admin-customers', to: '/admin/customers', label: '客户管理', desc: '客户资料与状态' },
]

const currentTitle = computed(() => route.meta.title || '管理后台')
const userName = computed(() => userStore.userInfo?.name || '管理员')

watch(
  () => route.fullPath,
  () => {
    sidebarOpen.value = false
  },
)

function isActive(item) {
  return item.name === 'admin-home'
    ? route.name === 'admin-home'
    : route.path.startsWith(item.to)
}

function logout() {
  userStore.logout()
  router.replace({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <Transition name="dialog">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-base-content/25 backdrop-blur-sm lg:hidden"
        @click="sidebarOpen = false"
      />
    </Transition>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-base-300 bg-base-100 transition-transform duration-200 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex h-16 items-center gap-3 border-b border-base-300 px-5">
        <div
          class="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold text-primary-content"
          style="background: var(--brand-gradient)"
        >
          A
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold">业务管理台</p>
          <p class="text-xs text-base-content/50">Admin Console</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 p-3">
        <RouterLink
          v-for="item in nav"
          :key="item.name"
          :to="item.to"
          class="block rounded-xl px-3 py-2.5 transition-colors"
          :class="
            isActive(item)
              ? 'bg-primary-soft text-primary'
              : 'text-base-content/70 hover:bg-base-200'
          "
        >
          <span class="block text-sm font-medium">{{ item.label }}</span>
          <span class="mt-0.5 block text-xs opacity-60">{{ item.desc }}</span>
        </RouterLink>
      </nav>

      <div class="border-t border-base-300 p-3">
        <RouterLink
          to="/"
          class="mb-2 block rounded-xl px-3 py-2 text-xs font-medium text-base-content/50 transition-colors hover:bg-base-200"
        >
          返回 H5 会员端
        </RouterLink>
        <button
          type="button"
          class="w-full rounded-xl px-3 py-2 text-left text-xs font-medium text-base-content/50 transition-colors hover:bg-base-200 hover:text-error"
          @click="logout"
        >
          退出登录
        </button>
      </div>
    </aside>

    <div class="lg:pl-64">
      <header
        class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-base-300 bg-base-100/90 px-4 backdrop-blur lg:px-8"
      >
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full text-base-content/60 transition-colors active:bg-base-200 lg:hidden"
            aria-label="打开菜单"
            @click="sidebarOpen = true"
          >
            ☰
          </button>
          <div>
            <p class="text-sm font-semibold">{{ currentTitle }}</p>
            <p class="text-xs text-base-content/50">运营管理</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="hidden text-right sm:block">
            <p class="text-sm font-medium">{{ userName }}</p>
            <p class="text-xs text-base-content/50">已登录</p>
          </div>
          <div
            class="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-content"
          >
            {{ userName.slice(0, 1) }}
          </div>
        </div>
      </header>

      <main class="p-4 lg:p-8">
        <div class="mx-auto w-full max-w-7xl">
          <router-view v-slot="{ Component }">
            <Transition name="page" mode="out-in">
              <component :is="Component" />
            </Transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>
