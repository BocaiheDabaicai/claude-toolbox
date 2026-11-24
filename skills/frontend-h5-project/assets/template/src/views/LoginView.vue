<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { safeRedirect } from '@/utils/redirect'
import { toast } from '@/utils/toast'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const form = reactive({ account: '', password: '' })
const submitting = ref(false)
const error = ref('')
const isDev = import.meta.env.DEV

// 从管理台跳到登录页时使用后台样式；H5 / PC 仍使用会员端登录视觉
const isAdminLogin = computed(() =>
  String(route.query.redirect || '').startsWith('/admin'),
)

const labelClass = computed(() =>
  isAdminLogin.value
    ? 'mb-1 block text-[13px] font-medium'
    : 'text-xs font-semibold text-base-content/55',
)
const fieldClass = computed(() =>
  isAdminLogin.value
    ? 'input input-bordered mt-1.5 w-full'
    : 'mt-1.5 h-11 w-full rounded-xl border border-base-300 bg-base-200/40 px-3 text-sm outline-none transition-colors placeholder:text-base-content/30 focus:border-primary focus:bg-base-100',
)
const errorClass = computed(() =>
  isAdminLogin.value
    ? 'rounded-md bg-error-soft px-3 py-2 text-[13px] text-error'
    : 'rounded-xl bg-error-soft px-3 py-2 text-xs leading-relaxed text-error',
)
const submitClass = computed(() =>
  isAdminLogin.value
    ? 'btn btn-primary w-full'
    : 'h-11 w-full rounded-full bg-primary text-sm font-semibold text-primary-content shadow-[0_6px_18px_rgba(78,150,214,0.28)] transition-transform active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100',
)
const demoBoxClass = computed(() =>
  isAdminLogin.value
    ? 'mt-5 rounded-md border border-dashed border-base-300 p-3'
    : 'mt-5 rounded-2xl border border-dashed border-base-300 p-3',
)
const demoButtonClass = computed(() =>
  isAdminLogin.value
    ? 'btn btn-outline btn-sm mt-2 w-full'
    : 'mt-2 h-9 w-full rounded-full border border-base-300 text-xs font-semibold text-base-content/60 transition-colors active:bg-base-200',
)

function redirectAfterLogin() {
  router.replace(safeRedirect(route.query.redirect))
}

async function submit() {
  if (submitting.value) return
  error.value = ''
  if (!form.account.trim() || !form.password) {
    error.value = '请输入账号和密码'
    return
  }
  submitting.value = true
  try {
    await userStore.login({ account: form.account.trim(), password: form.password })
    toast.success('登录成功')
    redirectAfterLogin()
  } catch (err) {
    error.value = err.message || '登录失败'
  } finally {
    submitting.value = false
  }
}

// 仅模板预览：接入真实登录接口后删除
function demoLogin() {
  userStore.loginDemo()
  redirectAfterLogin()
}
</script>

<template>
  <div
    :class="
      isAdminLogin
        ? 'admin-theme flex min-h-screen items-center justify-center bg-base-200 p-4'
        : 'flex min-h-screen flex-col bg-base-200'
    "
  >
    <div
      v-if="!isAdminLogin"
      class="relative overflow-hidden px-6 pb-16 pt-[calc(env(safe-area-inset-top)+4rem)] text-white"
      style="background: var(--brand-gradient)"
    >
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10" />
      <div class="absolute -bottom-16 -left-8 h-44 w-44 rounded-full bg-white/10" />
      <p class="relative text-sm font-medium tracking-[0.3em] opacity-80">WELCOME</p>
      <h1 class="relative mt-3 text-3xl font-bold leading-tight">欢迎登录</h1>
      <p class="relative mt-2 text-sm leading-relaxed opacity-80">这是模板登录页，接入目标后端后替换为真实登录流程。</p>
    </div>

    <main :class="isAdminLogin ? 'w-full max-w-sm' : 'relative -mt-8 flex-1 px-4 pb-10'">
      <div v-if="isAdminLogin" class="mb-6 text-center">
        <div
          class="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-base font-semibold text-primary-content"
        >
          A
        </div>
        <h1 class="text-xl font-semibold tracking-tight">业务管理后台</h1>
        <p class="mt-1 text-[13px] text-base-content/60">使用管理员账号登录</p>
      </div>

      <section
        :class="
          isAdminLogin
            ? 'panel p-6'
            : 'rounded-3xl bg-base-100 p-5 shadow-[0_16px_40px_rgba(42,59,87,0.12)]'
        "
      >
        <form class="space-y-4" @submit.prevent="submit">
          <label class="block">
            <span :class="labelClass">账号</span>
            <input
              v-model="form.account"
              type="text"
              autocomplete="username"
              placeholder="手机号 / 会员号 / 用户名"
              :class="fieldClass"
            />
          </label>

          <label class="block">
            <span :class="labelClass">密码</span>
            <input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              placeholder="请输入密码"
              :class="fieldClass"
            />
          </label>

          <p v-if="error" :class="errorClass">{{ error }}</p>

          <button type="submit" :class="submitClass" :disabled="submitting">
            {{ submitting ? '登录中...' : '登录' }}
          </button>
        </form>

        <div v-if="isDev" :class="demoBoxClass">
          <p class="text-[11px] leading-relaxed text-base-content/40">
            开发环境预览：模板尚未接入登录接口，可直接进入占位页面查看骨架；接入真实接口后删除此入口。
          </p>
          <button type="button" :class="demoButtonClass" @click="demoLogin">
            开发环境演示登录
          </button>
        </div>
      </section>
    </main>
  </div>
</template>
