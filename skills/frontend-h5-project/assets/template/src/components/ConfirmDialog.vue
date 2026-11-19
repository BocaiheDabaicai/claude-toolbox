<script setup>
import { confirmState, settleConfirm } from '@/utils/confirm'
</script>

<template>
  <Transition name="dialog">
    <div
      v-if="confirmState.open"
      class="fixed inset-0 z-[80] flex items-center justify-center bg-base-content/25 px-8 backdrop-blur-sm"
      @click.self="settleConfirm(false)"
    >
      <div class="dialog-card mx-auto w-full max-w-xs rounded-3xl bg-base-100 p-6 shadow-[0_16px_48px_rgba(40,70,110,0.24)]">
        <p class="text-lg font-bold">{{ confirmState.title }}</p>
        <p v-if="confirmState.message" class="mt-2 whitespace-pre-line text-sm leading-relaxed text-base-content/55">
          {{ confirmState.message }}
        </p>

        <div class="mt-6 flex gap-3">
          <button
            class="h-11 flex-1 rounded-2xl border border-base-300 text-sm font-semibold text-base-content/60 transition-transform active:scale-[0.98]"
            @click="settleConfirm(false)"
          >
            {{ confirmState.cancelText }}
          </button>
          <button
            class="h-11 flex-1 rounded-2xl text-sm font-semibold transition-transform active:scale-[0.98]"
            :class="confirmState.danger ? 'bg-error text-error-content' : 'bg-primary text-primary-content'"
            @click="settleConfirm(true)"
          >
            {{ confirmState.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>
