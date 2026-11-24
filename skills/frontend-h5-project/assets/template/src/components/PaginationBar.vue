<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  pageNum: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  unit: { type: String, default: '笔' },
  pageSizes: { type: Array, default: () => [10, 20, 50] },
})

const emit = defineEmits(['page-change', 'size-change'])

const totalPages = computed(() => Math.max(Math.ceil(props.total / props.pageSize), 1))
</script>

<template>
  <div v-if="total > 0" class="pagination-bar flex items-center justify-between gap-3 px-1">
    <p class="pagination-meta shrink-0 text-sm text-base-content/45">
      共 <span class="font-bold text-base-content">{{ total }}</span> {{ unit }}
      <slot />
    </p>

    <div class="flex items-center gap-2">
      <label class="relative block">
        <select
          class="pagination-size h-7 appearance-none rounded-full border border-base-300 bg-base-100 pl-2.5 pr-6 text-xs text-base-content/60 outline-none"
          :value="pageSize"
          aria-label="每页条数"
          @change="emit('size-change', Number($event.target.value))"
        >
          <option v-for="size in pageSizes" :key="size" :value="size">{{ size }} 条/页</option>
        </select>
        <svg
          viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          class="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-base-content/40"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </label>

      <button
        class="pagination-btn flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-35"
        :disabled="pageNum <= 1"
        aria-label="上一页"
        @click="emit('page-change', pageNum - 1)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
          <path d="m15 18-6-6 6-6" />
        </svg>
      </button>

      <span class="pagination-meta text-xs text-base-content/60">
        <span class="font-bold text-base-content">{{ pageNum }}</span> / {{ totalPages }}
      </span>

      <button
        class="pagination-btn flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-35"
        :disabled="pageNum >= totalPages"
        aria-label="下一页"
        @click="emit('page-change', pageNum + 1)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
          <path d="m9 18 6-6-6-6" />
        </svg>
      </button>
    </div>
  </div>
</template>
