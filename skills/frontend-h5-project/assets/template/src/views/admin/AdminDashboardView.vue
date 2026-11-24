<script setup>
import AdminNavIcon from '@/components/AdminNavIcon.vue'
import AdminPageHeader from '@/components/AdminPageHeader.vue'

const stats = [
  { label: '今日订单', value: '128', hint: '较昨日 +12.4%', icon: 'orders' },
  { label: '客户总数', value: '1,284', hint: '本月新增 36', icon: 'customers' },
  { label: '待处理', value: '6', hint: '需要跟进', icon: 'clock' },
]

const orders = [
  { id: 'SO-20261120-001', customer: '张明', amount: '¥ 2,890.00', status: 'paid', time: '10:24' },
  { id: 'SO-20261120-002', customer: '李静', amount: '¥ 560.00', status: 'pending', time: '10:08' },
  { id: 'SO-20261120-003', customer: '王强', amount: '¥ 1,280.00', status: 'paid', time: '09:42' },
  { id: 'SO-20261120-004', customer: '赵敏', amount: '¥ 320.00', status: 'refunded', time: '09:15' },
]

const statusMap = {
  paid: { label: '已支付', cls: 'badge-success' },
  pending: { label: '待支付', cls: 'badge-warning' },
  refunded: { label: '已退款', cls: 'badge-ghost' },
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
        <RouterLink to="/admin/customers" class="btn btn-primary btn-sm">
          管理客户
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div class="grid gap-4 sm:grid-cols-3">
      <section v-for="item in stats" :key="item.label" class="panel p-5">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-xs font-medium text-base-content/60">{{ item.label }}</p>
            <p class="mt-2 text-2xl font-semibold tabular-nums">{{ item.value }}</p>
          </div>
          <span
            class="flex h-8 w-8 items-center justify-center rounded-md bg-primary-soft text-primary"
          >
            <AdminNavIcon :name="item.icon" />
          </span>
        </div>
        <p class="mt-3 text-[11px] text-base-content/60">{{ item.hint }}</p>
      </section>
    </div>

    <div class="mt-4 grid gap-4 xl:grid-cols-[2fr_1fr]">
      <section class="panel overflow-hidden">
        <div class="flex items-center justify-between border-b border-base-300 px-5 py-3.5">
          <div>
            <h2 class="text-[13px] font-semibold">最近订单</h2>
            <p class="mt-0.5 text-[11px] text-base-content/60">示例数据，接入接口后替换</p>
          </div>
          <span class="rounded-full bg-base-200 px-2.5 py-1 text-[11px] font-medium text-base-content/60">
            {{ orders.length }} 条
          </span>
        </div>
        <div class="overflow-x-auto">
          <table class="table">
            <thead>
              <tr>
                <th>订单号</th>
                <th>客户</th>
                <th>金额</th>
                <th>状态</th>
                <th class="text-right">时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="text-[12px] text-base-content/60">{{ order.id }}</td>
                <td class="font-medium">{{ order.customer }}</td>
                <td class="tabular-nums">{{ order.amount }}</td>
                <td>
                  <span class="badge" :class="statusMap[order.status].cls">
                    {{ statusMap[order.status].label }}
                  </span>
                </td>
                <td class="text-right text-[13px] text-base-content/60">{{ order.time }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel p-5">
        <h2 class="text-[13px] font-semibold">快速入口</h2>
        <div class="mt-4 space-y-2">
          <RouterLink
            v-for="link in quickLinks"
            :key="link.to"
            :to="link.to"
            class="block rounded-md border border-base-300 px-4 py-3 transition-colors hover:border-primary/30 hover:bg-base-200"
          >
            <p class="text-[13px] font-medium">{{ link.title }}</p>
            <p class="mt-0.5 text-[11px] text-base-content/60">{{ link.desc }}</p>
          </RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>
