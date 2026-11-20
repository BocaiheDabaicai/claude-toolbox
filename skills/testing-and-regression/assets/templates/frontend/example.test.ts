import { describe, expect, it } from 'vitest'

// 示例：测试纯函数，而不是组件内部实现。
// 把 formatMoney 换成项目里的真实工具函数。
import { formatMoney } from '@/utils/money'

describe('formatMoney', () => {
  it('formats integer cents', () => {
    expect(formatMoney(12345)).toBe('123.45')
  })

  it('handles zero', () => {
    expect(formatMoney(0)).toBe('0.00')
  })
})
