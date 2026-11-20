<script setup lang="ts">
const config = useRuntimeConfig()
const { user } = useAuth()
useHead({ title: '设置' })
</script>

<template>
  <div>
    <PageHeader title="设置" description="账号、环境与运维信息" />

    <div class="grid gap-4 lg:grid-cols-2">
      <section class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <h2 class="text-sm font-semibold">当前账号</h2>
        <dl class="mt-4 space-y-3 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">姓名</dt>
            <dd class="font-medium">{{ user?.name }}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">邮箱</dt>
            <dd class="font-medium">{{ user?.email }}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">角色</dt>
            <dd class="font-medium">{{ user?.role }}</dd>
          </div>
        </dl>
      </section>

      <section class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <h2 class="text-sm font-semibold">运行信息</h2>
        <dl class="mt-4 space-y-3 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">应用</dt>
            <dd class="font-medium">{{ config.public.appName }}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">数据库</dt>
            <dd class="font-medium">PostgreSQL</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-base-content/50">健康检查</dt>
            <dd>
              <NuxtLink
                to="/api/healthz"
                target="_blank"
                class="link link-primary"
              >
                /api/healthz
              </NuxtLink>
            </dd>
          </div>
        </dl>
      </section>

      <section class="rounded-2xl border border-base-300 bg-base-100 p-5 lg:col-span-2">
        <h2 class="text-sm font-semibold">运维</h2>
        <p class="mt-2 text-sm leading-relaxed text-base-content/60">
          本项目自带
          <code class="rounded bg-base-200 px-1.5 py-0.5 text-xs">ops/project.toml</code>，
          可由
          <code class="rounded bg-base-200 px-1.5 py-0.5 text-xs">opsctl</code>
          统一启停、查看状态。修改端口、服务名或健康路径后，同步更新 manifest。
        </p>
      </section>
    </div>
  </div>
</template>
