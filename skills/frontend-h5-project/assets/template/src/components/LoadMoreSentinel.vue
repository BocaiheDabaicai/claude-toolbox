<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['load'])

const sentinel = ref(null)
let observer = null
let visible = false

function emitIfReady() {
  if (visible && !props.disabled) emit('load')
}

onMounted(() => {
  observer = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting
      emitIfReady()
    },
    { rootMargin: '240px 0px' },
  )
  if (sentinel.value) observer.observe(sentinel.value)
})

watch(
  () => props.disabled,
  () => {
    if (!props.disabled) emitIfReady()
  },
)

onUnmounted(() => observer?.disconnect())
</script>

<template>
  <div ref="sentinel" class="h-px w-full" />
</template>
