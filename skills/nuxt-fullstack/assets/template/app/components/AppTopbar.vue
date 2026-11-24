<script setup lang="ts">
import { USER_ROLE_LABELS } from '~~/shared/types/auth'

const route = useRoute()
const { user, logout } = useAuth()

const roleLabel = computed(() =>
  user.value ? USER_ROLE_LABELS[user.value.role] : '未登录',
)
const showRole = computed(
  () => !!user.value && roleLabel.value !== user.value.name,
)
const currentLabel = computed(() => findAdminNavLabel(route.path))
const initial = computed(() => (user.value?.name || '?').slice(0, 1))
</script>

<template>
  <header
    class="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-base-300 bg-base-100 px-4 lg:px-6"
  >
    <div class="flex min-w-0 items-center gap-2">
      <label
        for="app-drawer"
        class="btn btn-ghost btn-square btn-sm lg:hidden"
        aria-label="打开菜单"
      >
        <AppNavIcon name="menu" class="h-5 w-5" />
      </label>
      <div class="flex min-w-0 items-center gap-2">
        <span class="hidden text-[13px] text-base-content/55 sm:inline">管理后台</span>
        <span class="hidden text-base-content/20 sm:inline">/</span>
        <span class="truncate text-[13px] font-medium">{{ currentLabel }}</span>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <div class="hidden text-right sm:block">
        <p class="text-[13px] font-medium leading-tight">{{ user?.name || '未登录' }}</p>
        <p v-if="showRole" class="text-[11px] leading-tight text-base-content/60">
          {{ roleLabel }}
        </p>
      </div>
      <div class="dropdown dropdown-end">
        <button
          type="button"
          tabindex="0"
          class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-soft text-[12px] font-semibold text-primary ring-1 ring-primary/10"
        >
          {{ initial }}
        </button>
        <ul
          tabindex="0"
          class="menu dropdown-content z-50 mt-2 w-40 rounded-lg border border-base-300 bg-base-100 p-1.5 shadow-lg"
        >
          <li><NuxtLink to="/settings" class="text-[13px]">设置</NuxtLink></li>
          <li><button type="button" class="text-[13px]" @click="logout">退出登录</button></li>
        </ul>
      </div>
    </div>
  </header>
</template>
