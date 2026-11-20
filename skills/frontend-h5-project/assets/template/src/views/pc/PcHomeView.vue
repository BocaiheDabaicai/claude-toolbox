<script setup>
const features = [
  {
    title: '统一设计令牌',
    desc: 'H5、管理台、PC 共用 colors.css 与语义色，不再维护第二套主题。',
  },
  {
    title: '多布局切换',
    desc: 'H5 使用 max-w-md + 底栏，管理台使用侧边栏，PC 使用顶部导航与宽内容区。',
  },
  {
    title: '可复用交互',
    desc: 'Toast、Confirm、分页、骨架屏和表单模式在三种形态中保持一致。',
  },
]

const stats = [
  { value: '3', label: '界面形态' },
  { value: '1', label: '设计令牌' },
  { value: '0', label: '额外主题' },
]
</script>

<template>
  <div>
    <section class="relative overflow-hidden">
      <div class="absolute inset-0" style="background: var(--brand-gradient-air)" />
      <div class="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
        <p class="text-xs font-semibold tracking-[0.35em] text-primary">PRODUCT SUITE</p>
        <h1 class="mt-4 max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl">
          一套设计语言，
          <span class="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            覆盖 H5、管理后台与 PC
          </span>
        </h1>
        <p class="mt-5 max-w-2xl text-base leading-relaxed text-base-content/60">
          同一套 Vue 3 工程骨架，通过不同布局和路由分组适配移动端、运营后台和桌面站点。
          颜色、字体、动效和基础交互保持一致，业务页面按需组合。
        </p>
        <div class="mt-8 flex flex-col gap-3 sm:flex-row">
          <RouterLink
            to="/admin"
            class="inline-flex h-12 items-center justify-center rounded-full bg-primary px-6 text-sm font-semibold text-primary-content shadow-[0_6px_18px_rgba(78,150,214,0.28)] transition-transform active:scale-[0.98]"
          >
            进入管理后台
          </RouterLink>
          <RouterLink
            to="/"
            class="inline-flex h-12 items-center justify-center rounded-full border border-base-300 bg-base-100 px-6 text-sm font-semibold text-base-content/70 transition-colors hover:bg-base-200"
          >
            查看 H5 会员端
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="grid gap-4 md:grid-cols-3">
        <article
          v-for="feature in features"
          :key="feature.title"
          class="rounded-3xl border border-base-300 bg-base-100 p-6"
        >
          <div
            class="mb-4 flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-soft text-sm font-bold text-primary"
          >
            ✓
          </div>
          <h2 class="text-base font-semibold">{{ feature.title }}</h2>
          <p class="mt-2 text-sm leading-relaxed text-base-content/55">{{ feature.desc }}</p>
        </article>
      </div>
    </section>

    <section class="border-y border-base-300 bg-base-100">
      <div class="mx-auto grid max-w-7xl gap-6 px-4 py-12 sm:grid-cols-3 sm:px-6 lg:px-8">
        <div v-for="item in stats" :key="item.label" class="text-center">
          <p class="text-3xl font-semibold text-primary">{{ item.value }}</p>
          <p class="mt-1 text-xs text-base-content/45">{{ item.label }}</p>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div
        class="rounded-3xl p-8 text-white sm:p-12"
        style="background: var(--brand-gradient)"
      >
        <h2 class="text-2xl font-semibold">从同一个模板出发</h2>
        <p class="mt-3 max-w-2xl text-sm leading-relaxed text-white/85">
          在 `src/views` 下新增页面，在 `src/router/routes.js` 选择 H5、管理台或 PC 路由组。
          颜色只使用语义类，交互复用 Toast / Confirm / 分页组件。
        </p>
        <RouterLink
          to="/admin/customers"
          class="mt-6 inline-flex h-11 items-center justify-center rounded-full bg-white px-5 text-sm font-semibold text-primary"
        >
          查看客户管理示例
        </RouterLink>
      </div>
    </section>
  </div>
</template>
