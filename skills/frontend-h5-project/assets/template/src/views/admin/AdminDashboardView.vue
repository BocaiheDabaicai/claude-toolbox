<script setup>
import AdminPageHeader from '@/components/AdminPageHeader.vue'

const stats = [
  { label: '今日订单', value: '128', hint: '较昨日 +12.4%', tone: 'text-success' },
  { label: '客户总数', value: '1,284', hint: '本月新增 36', tone: 'text-primary' },
  { label: '待处理', value: '6', hint: '需要跟进', tone: 'text-warning' },
  { label: '系统状态', value: '正常', hint: 'API 与数据库可用', tone: 'text-success' },
]

const orders = [
  { id: 'SO-20261120-001', customer: '张明', amount: '¥ 2,890.00', status: 'paid', time: '10:24' },
  { id: 'SO-20261120-002', customer: '李静', amount: '¥ 560.00', status: 'pending', time: '10:08' },
  { id: 'SO-20261120-003', customer: '王强', amount: '¥ 1,280.00', status: 'paid', time: '09:42' },
  { id: 'SO-20261120-004', customer: '赵敏', amount: '¥ 320.00', status: 'refunded', time: '09:15' },
]

const statusMap = {
  paid: { label: '已支付', cls: 'bg-success-soft text-success' },
  pending: { label: '待支付', cls: 'bg-warning-soft text-warning' },
  refunded: { label: '已退款', cls: 'bg-base-200 text-base-content/50' },
}

const quickLinks = [
  { to: '/admin/customers', title: '管理客户', desc: '搜索、创建、编辑与删除客户资料' },
  { to: '/site', title: '查看 PC 站点', desc: '顶部导航 + 宽内容区示例' },
  { to: '/', title: '返回 H5 会员端', desc: '移动端 max-w-md + 底部导航' },
]
</script>

<template>
  <div>
    <AdminPageHeader title="仪表盘" description="业务概览与最近订单（示例数据）">
      <template #actions>
        <RouterLink
          to="/admin/customers"
          class="inline-flex h-10 items-center justify-center rounded-xl bg-primary px-4 text-sm font-semibold text-primary-content transition-opacity hover:opacity-90"
        >
          管理客户
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <section
        v-for="item in stats"
        :key="item.label"
        class="rounded-2xl border border-base-300 bg-base-100 p-5"
      >
        <p class="text-sm text-base-content/60">{{ item.label }}</p>
        <p class="mt-2 text-3xl font-semibold tabular-nums" :class="item.tone">
          {{ item.value }}
        </p>
        <p class="mt-1 text-xs text-base-content/40">{{ item.hint }}</p>
      </section>
    </div>

    <div class="mt-6 grid gap-4 xl:grid-cols-[2fr_1fr]">
      <section class="overflow-hidden rounded-2xl border border-base-300 bg-base-100">
        <div class="flex items-center justify-between border-b border-base-300 px-5 py-4">
          <div>
            <h2 class="text-sm font-semibold">最近订单</h2>
            <p class="mt-0.5 text-xs text-base-content/50">示例数据，接入接口后替换</p>
          </div>
          <span class="rounded-full bg-primary-soft px-3 py-1 text-xs font-medium text-primary">
            {{ orders.length }} 条
          </span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="text-xs text-base-content/45">
              <tr class="border-b border-base-300">
                <th class="px-5 py-3 font-medium">订单号</th>
                <th class="px-5 py-3 font-medium">客户</th>
                <th class="px-5 py-3 font-medium">金额</th>
                <th class="px-5 py-3 font-medium">状态</th>
                <th class="px-5 py-3 text-right font-medium">时间</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-base-300">
              <tr v-for="order in orders" :key="order.id" class="transition-colors hover:bg-base-200">
                <td class="px-5 py-3 font-mono text-xs text-base-content/60">{{ order.id }}</td>
                <td class="px-5 py-3 font-medium">{{ order.customer }}</td>
                <td class="px-5 py-3 tabular-nums">{{ order.amount }}</td>
                <td class="px-5 py-3">
                  <span
                    class="rounded-full px-2.5 py-1 text-xs font-medium"
                    :class="statusMap[order.status].cls"
                  >
                    {{ statusMap[order.status].label }}
                  </span>
                </td>
                <td class="px-5 py-3 text-right text-xs text-base-content/50">{{ order.time }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rounded-2xl border border-base-300 bg-base-100 p-5">
        <h2 class="text-sm font-semibold">快速入口</h2>
        <div class="mt-4 space-y-2">
          <RouterLink
            v-for="link in quickLinks"
            :key="link.to"
            :to="link.to"
            class="block rounded-xl border border-base-300 px-4 py-3 transition-colors hover:border-primary hover:bg-primary-soft"
          >
            <p class="text-sm font-medium">{{ link.title }}</p>
            <p class="mt-0.5 text-xs text-base-content/50">{{ link.desc }}</p>
          </RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>
