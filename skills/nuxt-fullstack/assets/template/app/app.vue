<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (title) =>
    title ? `${title} · __PROJECT_TITLE__` : '__PROJECT_TITLE__',
})
</script>
