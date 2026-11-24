<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center rounded-lg border border-dashed border-base-300 bg-base-100 px-6 py-12 text-center"
  >
    <div
      class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-base-200 text-base-content/35"
    >
      <span class="text-lg">∅</span>
    </div>
    <p class="text-[13px] font-medium">{{ title }}</p>
    <p v-if="description" class="mt-1 max-w-sm text-xs text-base-content/60">
      {{ description }}
    </p>
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>
