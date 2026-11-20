<script setup lang="ts">
const config = useRuntimeConfig()
const initial = computed(() => config.public.appName.slice(0, 1))
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-base-200 p-4">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-secondary text-lg font-bold text-primary-content shadow-sm">
          {{ initial }}
        </div>
        <h1 class="text-2xl font-semibold">{{ config.public.appName }}</h1>
        <p class="mt-1 text-sm text-base-content/60">业务管理后台</p>
      </div>
      <slot />
    </div>
  </div>
</template>
