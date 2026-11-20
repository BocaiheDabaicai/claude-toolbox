<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()
useHead({ title: `${props.error.statusCode} · 出错了` })
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-base-200 p-6 text-center">
    <p class="text-sm font-semibold tracking-[0.3em] text-primary">
      ERROR {{ error.statusCode }}
    </p>
    <h1 class="mt-3 text-2xl font-semibold">
      {{ error.statusMessage || '页面出错了' }}
    </h1>
    <p class="mt-2 max-w-md text-sm text-base-content/60">
      {{ error.message }}
    </p>
    <button
      type="button"
      class="btn btn-primary mt-6"
      @click="clearError({ redirect: '/' })"
    >
      返回首页
    </button>
  </div>
</template>
