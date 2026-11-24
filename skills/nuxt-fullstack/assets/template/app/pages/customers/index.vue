<script setup lang="ts">
import type { ApiResponse } from '~~/shared/types/api'
import type { Customer, CustomerList } from '~~/shared/types/customer'
import { customerInputSchema } from '~~/shared/schemas/customer'

useHead({ title: '客户' })

const page = ref(1)
const pageSize = ref(10)
const searchInput = ref('')
const search = ref('')

const { data, pending, error, refresh } = await useApiFetch<
  ApiResponse<CustomerList>
>('/api/customers', {
  key: 'customers:list',
  query: computed(() => ({
    page: page.value,
    pageSize: pageSize.value,
    search: search.value,
  })),
  watch: [page, pageSize, search],
})

const rows = computed(() => data.value?.data.rows ?? [])
const total = computed(() => data.value?.data.total ?? 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function applySearch() {
  search.value = searchInput.value.trim()
  page.value = 1
}

function changePage(next: number) {
  if (next < 1 || next > totalPages.value) return
  page.value = next
}

const modalOpen = ref(false)
const editing = ref<Customer | null>(null)
const saving = ref(false)
const formError = ref('')
const form = reactive({
  name: '',
  phone: '',
  email: '',
  company: '',
  note: '',
  status: 'active' as 'active' | 'inactive',
})

function resetForm() {
  form.name = ''
  form.phone = ''
  form.email = ''
  form.company = ''
  form.note = ''
  form.status = 'active'
  formError.value = ''
}

function openCreate() {
  editing.value = null
  resetForm()
  modalOpen.value = true
}

function openEdit(customer: Customer) {
  editing.value = customer
  form.name = customer.name
  form.phone = customer.phone ?? ''
  form.email = customer.email ?? ''
  form.company = customer.company ?? ''
  form.note = customer.note ?? ''
  form.status = customer.status
  formError.value = ''
  modalOpen.value = true
}

function closeModal() {
  if (saving.value) return
  modalOpen.value = false
}

async function save() {
  formError.value = ''
  const parsed = customerInputSchema.safeParse(form)
  if (!parsed.success) {
    formError.value = parsed.error.issues[0]?.message || '请检查表单'
    return
  }

  saving.value = true
  try {
    if (editing.value) {
      await $fetch(`/api/customers/${editing.value.id}`, {
        method: 'PUT',
        body: parsed.data,
      })
    } else {
      await $fetch('/api/customers', { method: 'POST', body: parsed.data })
    }
    modalOpen.value = false
    await refresh()
  } catch (err: unknown) {
    const body = err as { data?: { message?: string }; message?: string }
    formError.value = body.data?.message || body.message || '保存失败'
  } finally {
    saving.value = false
  }
}

async function remove(customer: Customer) {
  if (!window.confirm(`确定删除客户「${customer.name}」吗？`)) return
  try {
    await $fetch(`/api/customers/${customer.id}`, { method: 'DELETE' })
    await refresh()
  } catch (err: unknown) {
    const body = err as { data?: { message?: string }; message?: string }
    window.alert(body.data?.message || body.message || '删除失败')
  }
}
</script>

<template>
  <div>
    <PageHeader title="客户" description="客户资料、状态与检索">
      <template #actions>
        <button type="button" class="btn btn-primary btn-sm" @click="openCreate">
          新建客户
        </button>
      </template>
    </PageHeader>

    <div class="mb-4 flex flex-col gap-2 sm:flex-row">
      <form class="flex flex-1 gap-2" @submit.prevent="applySearch">
        <input
          v-model="searchInput"
          class="input input-bordered w-full sm:max-w-xs"
          placeholder="搜索姓名 / 电话 / 公司"
        />
        <button type="submit" class="btn btn-outline">搜索</button>
      </form>
      <button
        type="button"
        class="btn btn-ghost"
        :disabled="pending"
        @click="refresh"
      >
        刷新
      </button>
    </div>

    <div class="panel overflow-hidden">
      <div v-if="pending" class="space-y-3 p-5">
        <div v-for="i in 6" :key="i" class="skeleton h-10 w-full" />
      </div>
      <div v-else-if="error" class="p-5 text-sm text-error">
        加载失败：{{ error.message }}
      </div>
      <div v-else-if="rows.length === 0" class="p-5">
        <EmptyState
          title="没有找到客户"
          description="调整搜索条件，或创建第一个客户。"
        >
          <button type="button" class="btn btn-primary btn-sm" @click="openCreate">
            新建客户
          </button>
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
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in rows" :key="customer.id">
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
              <td class="text-right">
                <button
                  type="button"
                  class="btn btn-ghost btn-xs"
                  @click="openEdit(customer)"
                >
                  编辑
                </button>
                <button
                  type="button"
                  class="btn btn-ghost btn-xs text-error"
                  @click="remove(customer)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex items-center justify-between border-t border-base-300 px-4 py-3 text-sm">
        <span class="text-base-content/60">共 {{ total }} 条</span>
        <div class="join">
          <button
            class="btn btn-sm join-item"
            :disabled="page <= 1"
            @click="changePage(page - 1)"
          >
            上一页
          </button>
          <span class="btn btn-sm join-item pointer-events-none">
            {{ page }} / {{ totalPages }}
          </span>
          <button
            class="btn btn-sm join-item"
            :disabled="page >= totalPages"
            @click="changePage(page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <div v-if="modalOpen" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="text-base font-semibold">
          {{ editing ? '编辑客户' : '新建客户' }}
        </h3>

        <form class="mt-4 grid gap-4 sm:grid-cols-2" @submit.prevent="save">
          <label class="sm:col-span-2">
            <span class="mb-1 block text-sm font-medium">
              姓名 <span class="text-error">*</span>
            </span>
            <input
              v-model="form.name"
              class="input input-bordered w-full"
              placeholder="客户姓名"
            />
          </label>

          <label>
            <span class="mb-1 block text-sm font-medium">电话</span>
            <input
              v-model="form.phone"
              class="input input-bordered w-full"
              placeholder="手机号或座机"
            />
          </label>

          <label>
            <span class="mb-1 block text-sm font-medium">邮箱</span>
            <input
              v-model="form.email"
              type="email"
              class="input input-bordered w-full"
              placeholder="name@example.com"
            />
          </label>

          <label>
            <span class="mb-1 block text-sm font-medium">公司</span>
            <input
              v-model="form.company"
              class="input input-bordered w-full"
              placeholder="公司名称"
            />
          </label>

          <label>
            <span class="mb-1 block text-sm font-medium">状态</span>
            <select v-model="form.status" class="select select-bordered w-full">
              <option value="active">正常</option>
              <option value="inactive">停用</option>
            </select>
          </label>

          <label class="sm:col-span-2">
            <span class="mb-1 block text-sm font-medium">备注</span>
            <textarea
              v-model="form.note"
              class="textarea textarea-bordered h-24 w-full"
              placeholder="补充说明"
            ></textarea>
          </label>

          <p
            v-if="formError"
            class="rounded-md bg-error-soft px-3 py-2 text-[13px] text-error sm:col-span-2"
          >
            {{ formError }}
          </p>

          <div class="flex justify-end gap-2 sm:col-span-2">
            <button
              type="button"
              class="btn btn-ghost"
              :disabled="saving"
              @click="closeModal"
            >
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span
                v-if="saving"
                class="loading loading-spinner loading-sm"
              ></span>
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
      <div class="modal-backdrop" @click="closeModal"></div>
    </div>
  </div>
</template>
