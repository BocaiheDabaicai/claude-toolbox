<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const { user } = useAuth()
const initial = computed(() => config.public.appName.slice(0, 1))
const groups = computed(() => adminNavGroups(user.value?.role))

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}
</script>

<template>
  <aside class="rail flex min-h-full w-60 flex-col">
    <div class="rail-border flex h-14 items-center gap-2.5 border-b px-4">
      <div
        class="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-[13px] font-semibold text-primary-content"
      >
        {{ initial }}
      </div>
      <div class="min-w-0">
        <p class="rail-title truncate text-[13px] font-medium">
          {{ config.public.appName }}
        </p>
        <p class="rail-subtitle text-[11px] leading-tight">管理后台</p>
      </div>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-4">
      <div v-for="group in groups" :key="group.label" class="mb-5 last:mb-0">
        <p class="rail-label mb-1.5 px-2 text-[11px] font-medium tracking-wide">
          {{ group.label }}
        </p>
        <NuxtLink
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="rail-link relative flex h-9 items-center gap-2.5 rounded-md px-2 text-[13px] transition-colors"
          :class="{ 'is-active': isActive(item.to) }"
        >
          <span
            v-if="isActive(item.to)"
            class="absolute left-0 top-2.5 h-4 w-0.5 rounded-full bg-[var(--admin-accent)]"
          ></span>
          <AppNavIcon :name="item.icon" class="h-4 w-4 shrink-0 opacity-90" />
          <span class="truncate">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>

    <div class="rail-border border-t px-4 py-3">
      <p class="rail-label text-[11px]">v0.1 · 内部系统</p>
    </div>
  </aside>
</template>
