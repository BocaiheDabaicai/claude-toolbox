<script setup lang="ts">
defineProps<{
  name: string
}>()
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
    <template v-else-if="name === 'routes'">
      <path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3-6-3z" />
      <path d="M9 3v15" />
      <path d="M15 6v15" />
    </template>
    <template v-else-if="name === 'tasks'">
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V3h6v1" />
      <path d="M9 12l2 2 4-4" />
    </template>
    <template v-else-if="name === 'employees'">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c0-3.5 3.1-6 7-6s7 2.5 7 6" />
    </template>
    <template v-else-if="name === 'teams'">
      <circle cx="9" cy="8" r="3" />
      <path d="M3 19c0-3 2.7-5 6-5s6 2 6 5" />
      <path d="M16 5.5a3 3 0 0 1 0 5.8" />
      <path d="M18 14c2 .8 3 2.4 3 4.5" />
    </template>
    <template v-else-if="name === 'settings'">
      <path d="M4 7h9" />
      <path d="M18 7h2" />
      <circle cx="15.5" cy="7" r="2.5" />
      <path d="M4 17h2" />
      <path d="M11 17h9" />
      <circle cx="8.5" cy="17" r="2.5" />
    </template>
    <template v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </template>
    <template v-else-if="name === 'menu'">
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </template>
  </svg>
</template>
