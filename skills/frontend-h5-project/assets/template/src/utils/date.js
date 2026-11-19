export const WEEK_STARTS_MONDAY = ['一', '二', '三', '四', '五', '六', '日']
const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

export function pad2(value) {
  return String(value).padStart(2, '0')
}

export function todayDate() {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export function parseDate(value) {
  if (!value) return null
  const parts = String(value).split('-').map(Number)
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null
  const [year, month, day] = parts
  const date = new Date(year, month - 1, day)
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return null
  return date
}

export function parseMonth(value) {
  if (!value) return null
  const parts = String(value).split('-').map(Number)
  if (parts.length !== 2 || parts.some(Number.isNaN)) return null
  const [year, month] = parts
  if (month < 1 || month > 12) return null
  return { year, month }
}

export function formatDate(date) {
  return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`
}

// 后端时间可能是 "yyyy-MM-dd HH:mm:ss" 字符串，也可能是毫秒/秒时间戳；统一裁到分钟（可选到秒）
export function formatDateTime(value, withSeconds = false) {
  if (!value) return ''
  if (value instanceof Date) {
    const text = `${formatDate(value)} ${pad2(value.getHours())}:${pad2(value.getMinutes())}`
    return withSeconds ? `${text}:${pad2(value.getSeconds())}` : text
  }
  const text = String(value).trim()
  if (/^\d{10,13}$/.test(text)) {
    const numeric = Number(text)
    const date = new Date(numeric < 1e12 ? numeric * 1000 : numeric)
    if (!Number.isNaN(date.getTime())) return formatDateTime(date, withSeconds)
  }
  const normalized = text.replace('T', ' ')
  return withSeconds ? normalized.slice(0, 19) : normalized.slice(0, 16)
}

export function formatMonth(year, month) {
  return `${year}-${pad2(month)}`
}

export function formatMonthCN(year, month) {
  return `${year}年${month}月`
}

export function formatDateCN(value) {
  const date = value instanceof Date ? value : parseDate(value)
  if (!date) return ''
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 · 周${WEEKDAYS[date.getDay()]}`
}

export function addDays(date, days) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days)
}

export function addMonths(year, month, delta) {
  const target = new Date(year, month - 1 + delta, 1)
  return { year: target.getFullYear(), month: target.getMonth() + 1 }
}

export function startOfMonth(year, month) {
  return new Date(year, month - 1, 1)
}

export function endOfMonth(year, month) {
  return new Date(year, month, 0)
}

export function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate()
}

export function isSameDay(a, b) {
  return !!a && !!b && a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function utcDayNumber(date) {
  return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / 86400000
}

export function dayDiff(from, to) {
  return Math.round(utcDayNumber(to) - utcDayNumber(from))
}

export function rangeDayCount(start, end) {
  return dayDiff(start, end) + 1
}

export function isAfterDay(a, b) {
  return dayDiff(b, a) > 0
}

export function isAfterMonth(year, month, maxYear, maxMonth) {
  return year > maxYear || (year === maxYear && month > maxMonth)
}

// 固定 6 行 42 格，周一为每周第一天，前后不足的格子留空
export function calendarCells(year, month) {
  const offset = (new Date(year, month - 1, 1).getDay() + 6) % 7
  const total = daysInMonth(year, month)
  const cells = Array.from({ length: offset }, () => null)
  for (let day = 1; day <= total; day++) cells.push(new Date(year, month - 1, day))
  while (cells.length < 42) cells.push(null)
  return cells
}
