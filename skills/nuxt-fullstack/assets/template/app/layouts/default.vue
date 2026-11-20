<template>
  <div class="drawer min-h-screen bg-base-200 lg:drawer-open">
    <input id="app-drawer" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content flex min-h-screen flex-col">
      <AppTopbar />
      <main class="flex-1 p-4 lg:p-8">
        <div class="mx-auto w-full max-w-7xl">
          <slot />
        </div>
      </main>
    </div>
    <div class="drawer-side z-40">
      <label for="app-drawer" aria-label="关闭菜单" class="drawer-overlay"></label>
      <AppSidebar />
    </div>
  </div>
</template>
