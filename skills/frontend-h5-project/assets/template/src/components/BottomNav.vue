<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  activeName: { type: String, default: '' },
  // 例：{ cart: '3' }；由 App.vue 从对应 store 派生后传入
  badges: { type: Object, default: () => ({}) },
})

const route = useRoute()

const tabs = [
  {
    name: 'home',
    path: '/',
    label: '首页',
    icon: 'M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8',
  },
  {
    name: 'category',
    path: '/category',
    label: '分类',
    icon: 'M3 9l1.5-5h15L21 9M4 9v11h16V9M9 20v-6h6v6',
  },
  {
    name: 'cart',
    path: '/cart',
    label: '购物车',
    icon: 'M8 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2zM19 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2zM2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12',
  },
  {
    name: 'profile',
    path: '/profile',
    label: '我的',
    icon: 'M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  },
]

const currentName = computed(() => props.activeName || route.name)

function badgeOf(name) {
  return props.badges?.[name] || ''
}
</script>

<template>
  <div class="fixed inset-x-0 bottom-0 z-20">
    <nav class="mx-auto w-full max-w-md px-4 pb-[calc(env(safe-area-inset-bottom)+0.75rem)]">
      <div class="flex rounded-2xl border border-base-300/70 bg-base-100/90 p-1 shadow-lg shadow-primary/5 backdrop-blur">
        <RouterLink
          v-for="tab in tabs"
          :key="tab.name"
          :to="tab.path"
          class="flex flex-1 flex-col items-center gap-0.5 rounded-xl py-1.5 transition-colors"
          :class="currentName === tab.name ? 'bg-primary-soft text-primary' : 'text-base-content/40'"
        >
          <span class="relative">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
              <path :d="tab.icon" />
            </svg>
            <span
              v-if="badgeOf(tab.name)"
              class="absolute -right-2.5 -top-1.5 min-w-4 rounded-full bg-error px-1 text-center text-[10px] font-semibold leading-4 text-error-content shadow-sm"
            >
              {{ badgeOf(tab.name) }}
            </span>
          </span>
          <span class="text-xs font-medium">{{ tab.label }}</span>
        </RouterLink>
      </div>
    </nav>
  </div>
</template>
