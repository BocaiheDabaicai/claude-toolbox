<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

defineProps({
  title: { type: String, required: true },
  showHome: { type: Boolean, default: true },
})

const route = useRoute()
const router = useRouter()

const backTargets = computed(() => {
  const target = route.meta.backTo
  if (!target) return []
  return Array.isArray(target) ? target : [target]
})

// 静态路径和动态路径（如 /order/:orderId）都要能匹配上一页
function matchesTarget(name, path) {
  if (!path) return false
  const record = router.getRoutes().find((item) => item.name === name)
  if (!record) return false
  if (record.path === '/') return path === '/'
  const pattern = record.path
    .split('/')
    .map((segment) =>
      segment.startsWith(':')
        ? '[^/]+'
        : segment.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    )
    .join('/')
  return new RegExp(`^${pattern}/?$`).test(path)
}

// 上一页正好是上级时回退历史；否则跳转上级，避免停留在其他兄弟页面
function goBack() {
  const targets = backTargets.value
  const previousPath = (window.history.state?.back || '').split(/[?#]/)[0]
  if (targets.some((name) => matchesTarget(name, previousPath))) {
    router.back()
    return
  }
  if (!targets.length) {
    if (window.history.state?.back) router.back()
    else router.push({ name: 'home' })
    return
  }
  router.push({ name: targets[0] })
}
</script>

<template>
  <header class="sticky top-0 z-10 border-b border-base-300/60 bg-base-100/90 backdrop-blur">
    <div class="relative flex h-12 items-center justify-center px-4">
      <button
        class="absolute left-3 flex h-9 w-9 items-center justify-center rounded-full text-base-content/60 transition-colors active:bg-base-200"
        aria-label="返回"
        @click="goBack"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>
      <span class="text-base font-semibold">{{ title }}</span>
      <button
        v-if="showHome"
        class="absolute right-3 flex h-9 w-9 items-center justify-center rounded-full text-base-content/60 transition-colors active:bg-base-200"
        aria-label="返回首页"
        @click="$router.push('/')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
          <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
        </svg>
      </button>
    </div>
  </header>
</template>
