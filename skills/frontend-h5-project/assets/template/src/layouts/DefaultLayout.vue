<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const hideBottomNav = computed(() => route.meta.hideBottomNav)
// fullHeight 页面自己管理底部留白（如固定高度双栏布局），避免再叠加底栏 padding
const mainClass = computed(() => {
  if (route.meta.fullHeight) return 'pb-0'
  return hideBottomNav.value ? 'pb-6' : 'pb-28'
})
</script>

<template>
  <div class="mx-auto min-h-screen w-full max-w-md bg-base-100 sm:border-x sm:border-base-300 sm:shadow-[0_0_48px_rgba(46,110,173,0.08)]">
    <main :class="mainClass">
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
  </div>
</template>
