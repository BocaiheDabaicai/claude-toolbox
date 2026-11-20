<script setup lang="ts">
definePageMeta({ layout: 'auth' })
useHead({ title: '登录' })

const route = useRoute()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const pending = ref(false)
const error = ref('')

async function submit() {
  if (pending.value) return
  error.value = ''
  pending.value = true
  try {
    await login(email.value, password.value)
    const redirect =
      typeof route.query.redirect === 'string' &&
      route.query.redirect.startsWith('/')
        ? route.query.redirect
        : '/'
    await navigateTo(redirect)
  } catch (err: unknown) {
    const body = err as { data?: { message?: string }; message?: string }
    error.value = body.data?.message || body.message || '登录失败'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="card bg-base-100 shadow-xl">
    <form class="card-body gap-4" @submit.prevent="submit">
      <div>
        <h2 class="card-title text-lg">登录</h2>
        <p class="mt-1 text-sm text-base-content/60">
          使用管理员账号进入业务后台
        </p>
      </div>

      <label class="block">
        <span class="mb-1 block text-sm font-medium">邮箱</span>
        <input
          v-model="email"
          type="email"
          class="input input-bordered w-full"
          autocomplete="username"
          placeholder="admin@example.com"
          required
        />
      </label>

      <label class="block">
        <span class="mb-1 block text-sm font-medium">密码</span>
        <input
          v-model="password"
          type="password"
          class="input input-bordered w-full"
          autocomplete="current-password"
          placeholder="••••••••"
          required
        />
      </label>

      <p
        v-if="error"
        class="rounded-xl bg-error-soft px-3 py-2 text-sm text-error"
      >
        {{ error }}
      </p>

      <button type="submit" class="btn btn-primary w-full" :disabled="pending">
        <span
          v-if="pending"
          class="loading loading-spinner loading-sm"
        ></span>
        {{ pending ? '登录中…' : '登录' }}
      </button>

      <p class="text-center text-xs text-base-content/40">
        首次使用请先执行 pnpm db:seed
      </p>
    </form>
  </div>
</template>
