<script setup>
defineProps({
  rounded: { type: String, default: 'rounded-lg' },
  tone: { type: String, default: 'bg-base-300/70' },
})
</script>

<template>
  <div class="animate-pulse" :class="[tone, rounded]" />
</template>
