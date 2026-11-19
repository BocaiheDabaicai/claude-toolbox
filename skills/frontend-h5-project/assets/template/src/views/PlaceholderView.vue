<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'

const route = useRoute()
const title = computed(() => route.meta.title || String(route.name || '页面'))
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <PageHeader v-if="route.meta.hideBottomNav" :title="title" />

    <div class="space-y-3 px-4 pt-4">
      <section class="overflow-hidden rounded-3xl p-6 text-white shadow-[0_12px_32px_rgba(42,59,87,0.16)]" style="background: var(--brand-gradient)">
        <p class="text-[10px] font-semibold tracking-[0.35em] opacity-70">TEMPLATE</p>
        <h1 class="mt-2 text-2xl font-bold">{{ title }}</h1>
        <p class="mt-2 text-sm leading-relaxed opacity-85">
          这是工程骨架的占位页。在 <code class="rounded bg-white/15 px-1 py-0.5">src/views</code> 中创建业务页面，并在路由表登记。
        </p>
      </section>

      <section class="rounded-2xl bg-base-100 p-4 shadow-[0_2px_10px_rgba(42,59,87,0.04)]">
        <h2 class="text-sm font-semibold">当前路由</h2>
        <p class="mt-2 break-all rounded-xl bg-base-200/60 px-3 py-2 text-xs text-base-content/55">{{ route.fullPath }}</p>
        <h2 class="mt-4 text-sm font-semibold">下一步</h2>
        <ul class="mt-2 space-y-1.5 text-xs leading-relaxed text-base-content/55">
          <li>· 读取 Skill 的 references/architecture.md，确定请求层、登录态与路由结构。</li>
          <li>· 读取 references/ui-system.md，使用品牌色、字体、动效和图片加载规范。</li>
          <li>· 读取 references/patterns.md，复用列表、分页、购物车、库存等已验证模式。</li>
          <li>· 每完成一个页面执行 <code class="rounded bg-base-200 px-1">pnpm build</code>，并更新 docs/roadmap.md。</li>
        </ul>
      </section>
    </div>
  </div>
</template>
