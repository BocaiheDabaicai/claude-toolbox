<script setup lang="ts">
import type { ApiResponse } from '~~/shared/types/api'
import type { CustomerList } from '~~/shared/types/customer'
import { USER_ROLE_LABELS } from '~~/shared/types/auth'

useHead({ title: '仪表盘' })

const { user } = useAuth()

const { data, pending, error } = await useApiFetch<ApiResponse<CustomerList>>(
  '/api/customers',
  { key: 'dashboard:customers', query: { page: 1, pageSize: 5 } },
)

const total = computed(() => data.value?.data.total ?? 0)
const recent = computed(() => data.value?.data.rows ?? [])
const latest = computed(() => recent.value[0] ?? null)
const roleLabel = computed(() =>
  user.value ? USER_ROLE_LABELS[user.value.role] : '-',
)
</script>

<template>
  <div>
    <PageHeader title="仪表盘" description="业务概览与最近客户" />

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div class="panel p-5">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-xs font-medium text-base-content/60">客户总数</p>
            <p class="mt-2 text-2xl font-semibold tabular-nums">{{ total }}</p>
          </div>
          <span
            class="flex h-8 w-8 items-center justify-center rounded-md bg-primary-soft text-primary"
          >
            <AppNavIcon name="customers" />
          </span>
        </div>
        <p class="mt-3 text-[11px] text-base-content/60">不含已删除客户</p>
      </div>

      <div class="panel p-5">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-medium text-base-content/60">最近新增客户</p>
            <p class="mt-2 truncate text-xl font-semibold">
              {{ latest?.name || '—' }}
            </p>
          </div>
          <span
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary"
          >
            <AppNavIcon name="clock" />
          </span>
        </div>
        <p class="mt-3 text-[11px] text-base-content/60">
          {{ latest ? formatDateTime(latest.createdAt) : '暂无客户数据' }}
        </p>
      </div>

      <div class="panel p-5">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-medium text-base-content/60">当前账号</p>
            <p class="mt-2 truncate text-xl font-semibold">
              {{ user?.name || '未登录' }}
            </p>
          </div>
          <span
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary"
          >
            <AppNavIcon name="employees" />
          </span>
        </div>
        <p class="mt-3 text-[11px] text-base-content/60">{{ roleLabel }}</p>
      </div>
    </div>

    <div class="panel mt-4 overflow-hidden">
      <div class="flex items-center justify-between border-b border-base-300 px-5 py-3.5">
        <div>
          <h2 class="text-[13px] font-semibold">最近客户</h2>
          <p class="mt-0.5 text-[11px] text-base-content/60">按创建时间倒序</p>
        </div>
        <NuxtLink to="/customers" class="btn btn-ghost btn-sm text-primary">
          查看全部
        </NuxtLink>
      </div>

      <div v-if="pending" class="space-y-3 p-5">
        <div v-for="i in 4" :key="i" class="skeleton h-9 w-full" />
      </div>
      <div v-else-if="error" class="p-5 text-[13px] text-error">
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
              <td class="text-[13px] text-base-content/60">
                {{ formatDateTime(customer.createdAt) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
