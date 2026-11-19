import Big from 'big.js'

// 金额展示统一为 2–4 位小数：后端 4 位精度原样展示，仅超过 4 位时四舍五入
const MIN_FRACTION_DIGITS = 2
const MAX_FRACTION_DIGITS = 4

function isBlank(value) {
  return value === null || value === undefined || value === ''
}

function toBig(value) {
  return value instanceof Big ? value : new Big(value)
}

export function formatAmount(value, { min = MIN_FRACTION_DIGITS, max = MAX_FRACTION_DIGITS } = {}) {
  if (isBlank(value)) return '—'
  let big
  try {
    big = toBig(value)
  } catch {
    return '—'
  }
  const minDigits = Math.max(0, Math.min(min, max))
  const fixed = big.round(max, Big.roundHalfUp).toFixed(max)
  const negative = fixed.startsWith('-')
  const [intPart, rawFrac = ''] = (negative ? fixed.slice(1) : fixed).split('.')
  let frac = rawFrac.replace(/0+$/, '')
  if (frac.length < minDigits) frac = frac.padEnd(minDigits, '0')
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return `${negative ? '-' : ''}¥${grouped}${frac ? `.${frac}` : ''}`
}

export function formatSignedAmount(value) {
  if (isBlank(value)) return '—'
  let big
  try {
    big = toBig(value)
  } catch {
    return '—'
  }
  if (big.eq(0)) return formatAmount(0)
  return `${big.gt(0) ? '+' : '-'}${formatAmount(big.abs())}`
}

export function formatPercent(value, digits = 1) {
  if (isBlank(value)) return '—'
  try {
    return `${toBig(value).times(100).toFixed(digits)}%`
  } catch {
    return '—'
  }
}

export function sumAmounts(list, pick = (item) => item) {
  return list.reduce((total, item) => {
    const value = pick(item)
    return isBlank(value) ? total : total.plus(value)
  }, new Big(0))
}
