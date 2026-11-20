<script setup lang="ts">
import type { ApiResponse } from '~~/shared/types/api'
import type { CustomerList } from '~~/shared/types/customer'

useHead({ title: '仪表盘' })

const { data, pending, error } = await useApiFetch<ApiResponse<CustomerList>>(
  '/api/customers',
  { key: 'dashboard:customers', query: { page: 1, pageSize: 5 } },
)

const total = computed(() => data.value?.data.total ?? 0)
const recent = computed(() => data.value?.data.rows ?? [])
</script>

<template>
  <div>
    <PageHeader title="仪表盘" description="业务概览与最近客户" />

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <p class="text-sm text-base-content/60">客户总数</p>
        <p class="mt-2 text-3xl font-semibold tabular-nums">{{ total }}</p>
        <p class="mt-1 text-xs text-base-content/40">不含已删除客户</p>
      </div>
      <div class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <p class="text-sm text-base-content/60">数据库</p>
        <p class="mt-2 text-2xl font-semibold text-success">PostgreSQL</p>
        <p class="mt-1 text-xs text-base-content/40">直连 · Drizzle ORM</p>
      </div>
      <div class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <p class="text-sm text-base-content/60">认证</p>
        <p class="mt-2 text-2xl font-semibold">Cookie</p>
        <p class="mt-1 text-xs text-base-content/40">
          HttpOnly · SameSite=Lax
        </p>
      </div>
    </div>

    <div class="mt-6 rounded-2xl border border-base-300 bg-base-100">
      <div class="flex items-center justify-between border-b border-base-300 px-5 py-4">
        <div>
          <h2 class="text-sm font-semibold">最近客户</h2>
          <p class="mt-0.5 text-xs text-base-content/50">按创建时间倒序</p>
        </div>
        <NuxtLink to="/customers" class="btn btn-ghost btn-sm">
          查看全部
        </NuxtLink>
      </div>

      <div v-if="pending" class="space-y-3 p-5">
        <div v-for="i in 4" :key="i" class="skeleton h-10 w-full" />
      </div>
      <div v-else-if="error" class="p-5 text-sm text-error">
        加载失败：{{ error.message }}
      </div>
      <div v-else-if="recent.length === 0" class="p-5">
        <EmptyState
          title="还没有客户"
          description="先创建第一个客户，或执行 pnpm db:seed 生成示例数据。"
        >
          <NuxtLink to="/customers" class="btn btn-primary btn-sm">
            去创建
          </NuxtLink>
        </EmptyState>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>电话</th>
              <th>公司</th>
              <th>状态</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in recent" :key="customer.id">
              <td class="font-medium">{{ customer.name }}</td>
              <td>{{ customer.phone || '-' }}</td>
              <td>{{ customer.company || '-' }}</td>
              <td>
                <span
                  class="badge"
                  :class="
                    customer.status === 'active'
                      ? 'badge-success'
                      : 'badge-ghost'
                  "
                >
                  {{ customer.status === 'active' ? '正常' : '停用' }}
                </span>
              </td>
              <td class="text-sm text-base-content/50">
                {{ formatDateTime(customer.createdAt) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
