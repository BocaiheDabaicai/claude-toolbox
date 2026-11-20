<script setup>
import { computed, reactive, ref, watch } from 'vue'
import AdminPageHeader from '@/components/AdminPageHeader.vue'
import PaginationBar from '@/components/PaginationBar.vue'
import { confirm } from '@/utils/confirm'
import { toast } from '@/utils/toast'

let seed = 6
const rows = ref([
  { id: 1, name: '张明', phone: '13800000001', company: '远山科技', status: 'active', createdAt: '2026-11-18' },
  { id: 2, name: '李静', phone: '13800000002', company: '青禾贸易', status: 'active', createdAt: '2026-11-17' },
  { id: 3, name: '王强', phone: '13800000003', company: '恒信物流', status: 'inactive', createdAt: '2026-11-15' },
  { id: 4, name: '赵敏', phone: '13800000004', company: '云栖设计', status: 'active', createdAt: '2026-11-12' },
])

const search = ref('')
const statusFilter = ref('all')
const pageNum = ref(1)
const pageSize = ref(10)

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  return rows.value.filter((row) => {
    const matchKeyword =
      !keyword ||
      [row.name, row.phone, row.company].some((value) =>
        String(value || '').toLowerCase().includes(keyword),
      )
    const matchStatus = statusFilter.value === 'all' || row.status === statusFilter.value
    return matchKeyword && matchStatus
  })
})

const pageRows = computed(() => {
  const start = (pageNum.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

watch([search, statusFilter], () => {
  pageNum.value = 1
})

const modalOpen = ref(false)
const editingId = ref(null)
const form = reactive({ name: '', phone: '', company: '', status: 'active' })

function resetForm() {
  form.name = ''
  form.phone = ''
  form.company = ''
  form.status = 'active'
}

function openCreate() {
  editingId.value = null
  resetForm()
  modalOpen.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.name = row.name
  form.phone = row.phone
  form.company = row.company
  form.status = row.status
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
}

function save() {
  if (!form.name.trim()) {
    toast.error('请输入客户姓名')
    return
  }

  if (editingId.value) {
    const row = rows.value.find((item) => item.id === editingId.value)
    if (row) {
      Object.assign(row, {
        name: form.name.trim(),
        phone: form.phone.trim(),
        company: form.company.trim(),
        status: form.status,
      })
    }
    toast.success('已保存（示例数据）')
  } else {
    rows.value.unshift({
      id: seed++,
      name: form.name.trim(),
      phone: form.phone.trim(),
      company: form.company.trim(),
      status: form.status,
      createdAt: new Date().toISOString().slice(0, 10),
    })
    pageNum.value = 1
    toast.success('已创建（示例数据）')
  }
  closeModal()
}

async function remove(row) {
  const ok = await confirm({
    title: '删除客户',
    message: `确定删除「${row.name}」吗？`,
    danger: true,
  })
  if (!ok) return
  rows.value = rows.value.filter((item) => item.id !== row.id)
  const maxPage = Math.max(1, Math.ceil(filtered.value.length / pageSize.value))
  pageNum.value = Math.min(pageNum.value, maxPage)
  toast.success('已删除（示例数据）')
}

function changePage(next) {
  pageNum.value = next
}

function changeSize(next) {
  pageSize.value = next
  pageNum.value = 1
}

function statusLabel(status) {
  return status === 'active' ? '正常' : '停用'
}
</script>

<template>
  <div>
    <AdminPageHeader title="客户管理" description="列表、搜索、分页与表单示例；接入后端后替换为真实接口。">
      <template #actions>
        <button
          type="button"
          class="inline-flex h-10 items-center justify-center rounded-xl bg-primary px-4 text-sm font-semibold text-primary-content transition-opacity hover:opacity-90"
          @click="openCreate"
        >
          新建客户
        </button>
      </template>
    </AdminPageHeader>

    <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center">
      <input
        v-model="search"
        class="h-10 w-full rounded-xl border border-base-300 bg-base-100 px-3 text-sm outline-none transition-colors placeholder:text-base-content/30 focus:border-primary sm:max-w-xs"
        placeholder="搜索姓名 / 电话 / 公司"
      />
      <select
        v-model="statusFilter"
        class="h-10 rounded-xl border border-base-300 bg-base-100 px-3 text-sm text-base-content/70 outline-none focus:border-primary"
      >
        <option value="all">全部状态</option>
        <option value="active">正常</option>
        <option value="inactive">停用</option>
      </select>
      <span class="text-xs text-base-content/45">共 {{ filtered.length }} 位客户</span>
    </div>

    <div class="overflow-hidden rounded-2xl border border-base-300 bg-base-100">
      <div v-if="pageRows.length === 0" class="px-6 py-16 text-center">
        <p class="text-sm font-medium">没有找到客户</p>
        <p class="mt-1 text-xs text-base-content/50">调整搜索条件，或新建第一位客户。</p>
        <button
          type="button"
          class="mt-4 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-content"
          @click="openCreate"
        >
          新建客户
        </button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="text-xs text-base-content/45">
            <tr class="border-b border-base-300">
              <th class="px-5 py-3 font-medium">姓名</th>
              <th class="px-5 py-3 font-medium">电话</th>
              <th class="px-5 py-3 font-medium">公司</th>
              <th class="px-5 py-3 font-medium">状态</th>
              <th class="px-5 py-3 font-medium">创建时间</th>
              <th class="px-5 py-3 text-right font-medium">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-base-300">
            <tr
              v-for="row in pageRows"
              :key="row.id"
              class="transition-colors hover:bg-base-200"
            >
              <td class="px-5 py-3 font-medium">{{ row.name }}</td>
              <td class="px-5 py-3 text-base-content/70">{{ row.phone || '-' }}</td>
              <td class="px-5 py-3 text-base-content/70">{{ row.company || '-' }}</td>
              <td class="px-5 py-3">
                <span
                  class="rounded-full px-2.5 py-1 text-xs font-medium"
                  :class="
                    row.status === 'active'
                      ? 'bg-success-soft text-success'
                      : 'bg-base-200 text-base-content/50'
                  "
                >
                  {{ statusLabel(row.status) }}
                </span>
              </td>
              <td class="px-5 py-3 text-xs text-base-content/50">{{ row.createdAt }}</td>
              <td class="px-5 py-3 text-right">
                <button
                  type="button"
                  class="rounded-lg px-2.5 py-1.5 text-xs font-medium text-base-content/60 transition-colors hover:bg-base-200"
                  @click="openEdit(row)"
                >
                  编辑
                </button>
                <button
                  type="button"
                  class="rounded-lg px-2.5 py-1.5 text-xs font-medium text-error transition-colors hover:bg-error-soft"
                  @click="remove(row)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="border-t border-base-300 px-5 py-3">
        <PaginationBar
          :total="filtered.length"
          :page-num="pageNum"
          :page-size="pageSize"
          unit="位"
          @page-change="changePage"
          @size-change="changeSize"
        />
      </div>
    </div>

    <Transition name="dialog">
      <div
        v-if="modalOpen"
        class="fixed inset-0 z-[80] flex items-center justify-center bg-base-content/25 px-4 backdrop-blur-sm"
        @click.self="closeModal"
      >
        <div
          class="dialog-card w-full max-w-lg rounded-3xl bg-base-100 p-6 shadow-[0_16px_48px_rgba(40,70,110,0.24)]"
        >
          <h2 class="text-lg font-semibold">{{ editingId ? '编辑客户' : '新建客户' }}</h2>
          <form class="mt-4 grid gap-4 sm:grid-cols-2" @submit.prevent="save">
            <label class="sm:col-span-2">
              <span class="mb-1 block text-sm font-medium">姓名 <span class="text-error">*</span></span>
              <input
                v-model="form.name"
                class="h-10 w-full rounded-xl border border-base-300 bg-base-100 px-3 text-sm outline-none focus:border-primary"
                placeholder="客户姓名"
              />
            </label>
            <label>
              <span class="mb-1 block text-sm font-medium">电话</span>
              <input
                v-model="form.phone"
                class="h-10 w-full rounded-xl border border-base-300 bg-base-100 px-3 text-sm outline-none focus:border-primary"
                placeholder="手机号或座机"
              />
            </label>
            <label>
              <span class="mb-1 block text-sm font-medium">公司</span>
              <input
                v-model="form.company"
                class="h-10 w-full rounded-xl border border-base-300 bg-base-100 px-3 text-sm outline-none focus:border-primary"
                placeholder="公司名称"
              />
            </label>
            <label>
              <span class="mb-1 block text-sm font-medium">状态</span>
              <select
                v-model="form.status"
                class="h-10 w-full rounded-xl border border-base-300 bg-base-100 px-3 text-sm outline-none focus:border-primary"
              >
                <option value="active">正常</option>
                <option value="inactive">停用</option>
              </select>
            </label>
            <div class="flex items-end justify-end gap-2">
              <button
                type="button"
                class="h-10 rounded-xl border border-base-300 px-4 text-sm font-medium text-base-content/60 transition-colors hover:bg-base-200"
                @click="closeModal"
              >
                取消
              </button>
              <button
                type="submit"
                class="h-10 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-content transition-opacity hover:opacity-90"
              >
                保存
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>
