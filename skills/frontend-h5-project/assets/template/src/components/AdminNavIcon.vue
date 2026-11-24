<script setup>
defineProps({
  name: { type: String, required: true },
})
</script>

<template>
  <svg
    class="h-4 w-4"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="name === 'dashboard'">
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </template>
    <template v-else-if="name === 'customers'">
      <path d="M4 9l1.5-5h13L20 9" />
      <path d="M5 9v11h14V9" />
      <path d="M9 20v-5h6v5" />
      <path d="M4 9c0 1.1.9 2 2 2s2-.9 2-2c0 1.1.9 2 2 2s2-.9 2-2c0 1.1.9 2 2 2s2-.9 2-2c0 1.1.9 2 2 2s2-.9 2-2" />
    </template>
    <template v-else-if="name === 'orders'">
      <path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3z" />
      <path d="M9 8h6" />
      <path d="M9 12h6" />
    </template>
    <template v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </template>
    <template v-else-if="name === 'settings'">
      <path d="M4 7h9" />
      <path d="M18 7h2" />
      <circle cx="15.5" cy="7" r="2.5" />
      <path d="M4 17h2" />
      <path d="M11 17h9" />
      <circle cx="8.5" cy="17" r="2.5" />
    </template>
    <template v-else-if="name === 'menu'">
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </template>
  </svg>
</template>
