<script setup>
const nav = [
  { to: '/site', label: '首页' },
  { to: '/admin', label: '管理后台' },
  { to: '/', label: '会员端' },
]
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <header class="sticky top-0 z-30 border-b border-base-300 bg-base-100/90 backdrop-blur">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <RouterLink to="/site" class="flex items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold text-primary-content"
            style="background: var(--brand-gradient)"
          >
            A
          </div>
          <span class="text-sm font-semibold">PC 站点</span>
        </RouterLink>

        <nav class="hidden items-center gap-1 md:flex">
          <RouterLink
            v-for="item in nav"
            :key="item.to"
            :to="item.to"
            class="rounded-full px-4 py-2 text-sm font-medium text-base-content/60 transition-colors hover:bg-base-200 hover:text-base-content"
          >
            {{ item.label }}
          </RouterLink>
        </nav>

        <RouterLink
          to="/"
          class="rounded-full border border-base-300 px-4 py-2 text-sm font-medium text-base-content/70 transition-colors hover:bg-base-200"
        >
          会员端
        </RouterLink>
      </div>
    </header>

    <main>
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>

    <footer class="border-t border-base-300 bg-base-100 py-8 text-center text-xs text-base-content/40">
      © 2026 PC 站点 · 与 H5 / 管理台共用设计令牌
    </footer>
  </div>
</template>
