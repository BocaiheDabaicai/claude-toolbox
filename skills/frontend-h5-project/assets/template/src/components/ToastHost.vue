<script setup>
import { toastState, dismiss } from '@/utils/toast'

const ICONS = {
  info: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 16v-4M12 8h.01',
  success: 'M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4 12 14.01l-3-3',
  error: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 8v4M12 16h.01',
}
const TINTS = { info: 'text-primary', success: 'text-success', error: 'text-error' }
</script>

<template>
  <div class="pointer-events-none fixed inset-x-0 top-0 z-[70] mx-auto w-full max-w-md px-6 pt-[calc(env(safe-area-inset-top)+1rem)]">
    <TransitionGroup name="toast" tag="div" class="flex flex-col items-center gap-2">
      <button
        v-for="item in toastState.items"
        :key="item.id"
        class="pointer-events-auto flex w-full items-center gap-2.5 rounded-2xl border border-base-300/70 bg-base-100/95 px-4 py-3 text-left shadow-[0_8px_24px_rgba(70,110,150,0.18)] backdrop-blur transition-transform active:scale-[0.98]"
        @click="dismiss(item.id)"
      >
        <svg
          viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
          class="h-4.5 w-4.5 shrink-0" :class="TINTS[item.type]"
        >
          <path :d="ICONS[item.type]" />
        </svg>
        <span class="min-w-0 flex-1 text-sm font-medium">{{ item.message }}</span>
      </button>
    </TransitionGroup>
  </div>
</template>
