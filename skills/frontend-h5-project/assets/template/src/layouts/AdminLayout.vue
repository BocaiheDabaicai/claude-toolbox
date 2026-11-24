<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminNavIcon from '@/components/AdminNavIcon.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarOpen = ref(false)

const navGroups = [
  {
    label: '业务',
    items: [
      { name: 'admin-home', to: '/admin', label: '仪表盘', icon: 'dashboard' },
      {
        name: 'admin-customers',
        to: '/admin/customers',
        label: '客户管理',
        icon: 'customers',
      },
    ],
  },
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
  router.replace({ name: 'login', query: { redirect: '/admin' } })
}
</script>

<template>
  <div class="admin-theme min-h-screen bg-base-200">
    <Transition name="dialog">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-base-content/30 lg:hidden"
        @click="sidebarOpen = false"
      />
    </Transition>

    <aside
      class="rail fixed inset-y-0 left-0 z-50 flex w-60 flex-col transition-transform duration-200 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="rail-border flex h-14 items-center gap-2.5 border-b px-4">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-[13px] font-semibold text-primary-content"
        >
          A
        </div>
        <div class="min-w-0">
          <p class="rail-title truncate text-[13px] font-medium">业务管理台</p>
          <p class="rail-subtitle text-[11px] leading-tight">管理后台</p>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto px-3 py-4">
        <div v-for="group in navGroups" :key="group.label" class="mb-5 last:mb-0">
          <p class="rail-label mb-1.5 px-2 text-[11px] font-medium tracking-wide">
            {{ group.label }}
          </p>
          <RouterLink
            v-for="item in group.items"
            :key="item.name"
            :to="item.to"
            class="rail-link relative flex h-9 items-center gap-2.5 rounded-md px-2 text-[13px] transition-colors"
            :class="{ 'is-active': isActive(item) }"
          >
            <span
              v-if="isActive(item)"
              class="absolute left-0 top-2.5 h-4 w-0.5 rounded-full bg-[var(--admin-accent)]"
            ></span>
            <AdminNavIcon :name="item.icon" class="h-4 w-4 shrink-0 opacity-90" />
            <span class="truncate">{{ item.label }}</span>
          </RouterLink>
        </div>
      </nav>

      <div class="rail-border space-y-1 border-t px-3 py-3">
        <RouterLink
          to="/"
          class="rail-link flex h-8 items-center rounded-md px-2 text-[12px] transition-colors"
        >
          返回 H5 会员端
        </RouterLink>
        <button
          type="button"
          class="rail-link flex h-8 w-full items-center rounded-md px-2 text-left text-[12px] transition-colors"
          @click="logout"
        >
          退出登录
        </button>
        <p class="rail-label px-2 pt-1 text-[11px]">v0.1 · 内部系统</p>
      </div>
    </aside>

    <div class="lg:pl-60">
      <header
        class="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-base-300 bg-base-100 px-4 lg:px-6"
      >
        <div class="flex min-w-0 items-center gap-2">
          <button
            type="button"
            class="btn btn-ghost btn-square btn-sm lg:hidden"
            aria-label="打开菜单"
            @click="sidebarOpen = true"
          >
            <AdminNavIcon name="menu" class="h-5 w-5" />
          </button>
          <div class="flex min-w-0 items-center gap-2">
            <span class="hidden text-[13px] text-base-content/55 sm:inline">管理后台</span>
            <span class="hidden text-base-content/20 sm:inline">/</span>
            <span class="truncate text-[13px] font-medium">{{ currentTitle }}</span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="hidden text-right sm:block">
            <p class="text-[13px] font-medium leading-tight">{{ userName }}</p>
            <p class="text-[11px] leading-tight text-base-content/60">已登录</p>
          </div>
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-soft text-[12px] font-semibold text-primary ring-1 ring-primary/10"
          >
            {{ userName.slice(0, 1) }}
          </div>
        </div>
      </header>

      <main class="p-4 lg:p-6">
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
