import { reactive } from 'vue'

export const confirmState = reactive({
  open: false,
  title: '',
  message: '',
  confirmText: '确认',
  cancelText: '取消',
  danger: false,
})

let resolver = null

// 用法：if (await confirm({ title, message, danger: true })) { ... }
export function confirm({ title = '确认操作', message = '', confirmText = '确认', cancelText = '取消', danger = false } = {}) {
  Object.assign(confirmState, { open: true, title, message, confirmText, cancelText, danger })
  return new Promise((resolve) => {
    resolver = resolve
  })
}

export function settleConfirm(result) {
  confirmState.open = false
  resolver?.(result)
  resolver = null
}
