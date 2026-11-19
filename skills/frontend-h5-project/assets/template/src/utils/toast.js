import { reactive } from 'vue'

export const toastState = reactive({ items: [] })

let seed = 0
const DURATION = { info: 2000, success: 2000, error: 2400 }

function push(message, type) {
  if (!message) return
  const id = ++seed
  toastState.items.push({ id, message, type })
  setTimeout(() => dismiss(id), DURATION[type] ?? 2000)
}

export function dismiss(id) {
  const index = toastState.items.findIndex((item) => item.id === id)
  if (index > -1) toastState.items.splice(index, 1)
}

export const toast = {
  info: (message) => push(message, 'info'),
  success: (message) => push(message, 'success'),
  error: (message) => push(message, 'error'),
}
