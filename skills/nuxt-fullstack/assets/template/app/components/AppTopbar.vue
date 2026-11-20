<script setup lang="ts">
const config = useRuntimeConfig()
const { user, logout } = useAuth()
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-base-300 bg-base-100/90 px-4 backdrop-blur lg:px-8">
    <div class="flex items-center gap-3">
      <label for="app-drawer" class="btn btn-ghost btn-sm lg:hidden" aria-label="打开菜单">
        <span class="text-lg">☰</span>
      </label>
      <div>
        <p class="text-sm font-semibold">{{ config.public.appName }}</p>
        <p class="text-xs text-base-content/50">运营管理</p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <div class="hidden text-right sm:block">
        <p class="text-sm font-medium">{{ user?.name || '未登录' }}</p>
        <p class="text-xs text-base-content/50">{{ user?.email }}</p>
      </div>
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="avatar placeholder btn btn-ghost btn-circle">
          <div class="w-9 rounded-full bg-primary text-primary-content">
            <span>{{ (user?.name || '?').slice(0, 1) }}</span>
          </div>
        </div>
        <ul tabindex="0" class="menu dropdown-content z-50 mt-3 w-44 rounded-box bg-base-100 p-2 shadow">
          <li><NuxtLink to="/settings">设置</NuxtLink></li>
          <li><button type="button" @click="logout">退出登录</button></li>
        </ul>
      </div>
    </div>
  </header>
</template>
