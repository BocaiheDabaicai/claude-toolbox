<script setup lang="ts">
const config = useRuntimeConfig()
const initial = computed(() => config.public.appName.slice(0, 1))
</script>

<template>
  <div class="admin-theme flex min-h-screen items-center justify-center bg-base-200 p-4">
    <div class="w-full max-w-sm">
      <div class="mb-6 text-center">
        <div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-base font-semibold text-primary-content">
          {{ initial }}
        </div>
        <h1 class="text-xl font-semibold tracking-tight">{{ config.public.appName }}</h1>
        <p class="mt-1 text-[13px] text-base-content/60">业务管理后台</p>
      </div>
      <slot />
    </div>
  </div>
</template>
