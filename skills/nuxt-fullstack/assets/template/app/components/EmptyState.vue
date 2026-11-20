<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-base-300 bg-base-100 px-6 py-14 text-center">
    <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-base-200 text-base-content/40">
      <span class="text-xl">∅</span>
    </div>
    <p class="text-sm font-medium">{{ title }}</p>
    <p v-if="description" class="mt-1 max-w-sm text-xs text-base-content/50">
      {{ description }}
    </p>
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>
