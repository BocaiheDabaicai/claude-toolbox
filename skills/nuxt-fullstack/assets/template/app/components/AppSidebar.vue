<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const initial = computed(() => config.public.appName.slice(0, 1))

const items = [
  { to: '/', label: '仪表盘', desc: '业务总览' },
  { to: '/customers', label: '客户', desc: '客户资料与状态' },
  { to: '/settings', label: '设置', desc: '账号与环境' },
]

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}
</script>

<template>
  <aside class="flex min-h-full w-64 flex-col border-r border-base-300 bg-base-100">
    <div class="flex h-16 items-center gap-3 border-b border-base-300 px-5">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-secondary text-sm font-bold text-primary-content">
        {{ initial }}
      </div>
      <div class="min-w-0">
        <p class="truncate text-sm font-semibold">{{ config.public.appName }}</p>
        <p class="text-xs text-base-content/50">管理后台</p>
      </div>
    </div>

    <nav class="flex-1 space-y-1 p-3">
      <NuxtLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="block rounded-xl px-3 py-2.5 transition-colors"
        :class="
          isActive(item.to)
            ? 'bg-primary-soft text-primary'
            : 'text-base-content/70 hover:bg-base-200'
        "
      >
        <span class="block text-sm font-medium">{{ item.label }}</span>
        <span class="mt-0.5 block text-xs opacity-60">{{ item.desc }}</span>
      </NuxtLink>
    </nav>

    <div class="border-t border-base-300 p-4 text-xs text-base-content/40">
      Nuxt 4 · 直连 PostgreSQL
    </div>
  </aside>
</template>
