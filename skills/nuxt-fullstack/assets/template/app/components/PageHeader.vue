<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <h1 class="text-xl font-semibold tracking-tight">{{ title }}</h1>
      <p v-if="description" class="mt-1 text-[13px] text-base-content/60">
        {{ description }}
      </p>
    </div>
    <div class="page-actions">
      <slot name="actions" />
    </div>
  </div>
</template>
