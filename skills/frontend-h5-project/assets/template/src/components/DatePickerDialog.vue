<script setup>
import { computed, ref, watch } from 'vue'
import {
  WEEK_STARTS_MONDAY,
  addDays,
  addMonths,
  calendarCells,
  dayDiff,
  endOfMonth,
  formatDate,
  formatDateCN,
  formatMonth,
  formatMonthCN,
  isAfterDay,
  isAfterMonth,
  isSameDay,
  parseDate,
  parseMonth,
  rangeDayCount,
  startOfMonth,
  todayDate,
} from '@/utils/date'

const props = defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: 'date' },
  value: { type: [String, Object], default: null },
  maxDate: { type: String, default: '' },
  minDate: { type: String, default: '' },
  showPresets: { type: Boolean, default: true },
})

const emit = defineEmits(['close', 'confirm'])

const pickerMode = computed(() => (['month', 'date', 'range'].includes(props.mode) ? props.mode : 'date'))
const pickerTitle = computed(() => ({ month: '选择年月', date: '选择日期', range: '选择日期范围' })[pickerMode.value])
const maxDay = computed(() => parseDate(props.maxDate) || todayDate())
const maxYear = computed(() => maxDay.value.getFullYear())
const maxMonth = computed(() => maxDay.value.getMonth() + 1)
const minDay = computed(() => parseDate(props.minDate))
const minYear = computed(() => (minDay.value ? minDay.value.getFullYear() : 1900))
const minMonth = computed(() => (minDay.value ? minDay.value.getMonth() + 1 : 1))
const today = todayDate()

const draftDate = ref(null)
const rangeStart = ref(null)
const rangeEnd = ref(null)
const draftYear = ref(today.getFullYear())
const draftMonth = ref(today.getMonth() + 1)
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth() + 1)
const panel = ref('calendar')

function initDraft() {
  const now = todayDate()
  panel.value = pickerMode.value === 'month' ? 'months' : 'calendar'

  if (pickerMode.value === 'month') {
    const parsed = parseMonth(props.value)
    draftYear.value = parsed?.year ?? now.getFullYear()
    draftMonth.value = parsed?.month ?? now.getMonth() + 1
    viewYear.value = draftYear.value
    viewMonth.value = draftMonth.value
    return
  }

  if (pickerMode.value === 'date') {
    let parsed = parseDate(props.value) || now
    if (isAfterDay(parsed, maxDay.value)) parsed = maxDay.value
    if (minDay.value && isAfterDay(minDay.value, parsed)) parsed = minDay.value
    draftDate.value = parsed
    viewYear.value = parsed.getFullYear()
    viewMonth.value = parsed.getMonth() + 1
    return
  }

  const start = parseDate(props.value?.start)
  const end = parseDate(props.value?.end)
  rangeStart.value = start
  rangeEnd.value = end
  const base = end || start || now
  viewYear.value = base.getFullYear()
  viewMonth.value = base.getMonth() + 1
}

watch(
  () => props.open,
  (open) => {
    if (open) initDraft()
  },
  { immediate: true },
)

const shownYear = computed(() => (pickerMode.value === 'month' ? draftYear.value : viewYear.value))
const selectedPanelMonth = computed(() => (pickerMode.value === 'month' ? draftMonth.value : viewMonth.value))
const selectedPanelDisabled = computed(() => isDisabledMonth(shownYear.value, selectedPanelMonth.value))
const atMaxMonth = computed(() => viewYear.value === maxYear.value && viewMonth.value >= maxMonth.value)
const atMinMonth = computed(() => viewYear.value === minYear.value && viewMonth.value <= minMonth.value)
const atMaxPanelYear = computed(() => shownYear.value >= maxYear.value)
const atMinPanelYear = computed(() => shownYear.value <= minYear.value)
const yearOptions = computed(() => {
  const years = []
  for (let year = maxYear.value; year >= minYear.value; year -= 1) years.push(year)
  return years
})
const cells = computed(() => calendarCells(viewYear.value, viewMonth.value))
const monthTitle = computed(() => formatMonthCN(viewYear.value, viewMonth.value))

const presets = computed(() => {
  if (pickerMode.value === 'month') {
    return [
      { key: 'thisMonth', label: '本月' },
      { key: 'lastMonth', label: '上月' },
    ]
  }
  if (pickerMode.value === 'range') {
    return [
      { key: 'thisYear', label: '本年' },
      { key: 'thisMonth', label: '本月' },
      { key: 'lastMonth', label: '上月' },
      { key: 'last7', label: '近7天' },
      { key: 'last30', label: '近30天' },
    ]
  }
  return [{ key: 'today', label: '今天' }]
})

const summary = computed(() => {
  if (pickerMode.value === 'month') return formatMonthCN(draftYear.value, draftMonth.value)
  if (pickerMode.value === 'date') return draftDate.value ? formatDateCN(draftDate.value) : '请选择日期'
  if (!rangeStart.value) return '请选择开始日期'
  if (!rangeEnd.value) return `${formatDate(rangeStart.value)} ~ 请选择结束日期`
  return `${formatDate(rangeStart.value)} ~ ${formatDate(rangeEnd.value)} · 共 ${rangeDayCount(rangeStart.value, rangeEnd.value)} 天`
})

const canConfirm = computed(() => {
  if (pickerMode.value === 'month') return !isDisabledMonth(draftYear.value, draftMonth.value)
  if (pickerMode.value === 'date') return !!draftDate.value && !isDisabledDay(draftDate.value)
  return !!rangeStart.value && !!rangeEnd.value && !isDisabledDay(rangeEnd.value)
})

function isDisabledDay(date) {
  if (!date) return true
  if (minDay.value && isAfterDay(minDay.value, date)) return true
  return isAfterDay(date, maxDay.value)
}

function isDisabledMonth(year, month) {
  if (year < minYear.value || (year === minYear.value && month < minMonth.value)) return true
  return isAfterMonth(year, month, maxYear.value, maxMonth.value)
}

function isEndpoint(date) {
  if (pickerMode.value === 'date') return isSameDay(date, draftDate.value)
  return isSameDay(date, rangeStart.value) || isSameDay(date, rangeEnd.value)
}

function isInRange(date) {
  return (
    pickerMode.value === 'range' &&
    !!rangeStart.value &&
    !!rangeEnd.value &&
    dayDiff(rangeStart.value, date) > 0 &&
    dayDiff(date, rangeEnd.value) > 0
  )
}

function isTodayDay(date) {
  return isSameDay(date, today)
}

function dayClasses(date) {
  if (isEndpoint(date)) return 'bg-primary font-semibold text-primary-content shadow-sm'
  if (isInRange(date)) return 'bg-primary-soft text-primary'
  if (isTodayDay(date)) return 'bg-primary-soft font-semibold text-primary ring-1 ring-primary/30'
  if (isDisabledDay(date)) return 'text-base-content/20'
  return 'text-base-content active:bg-base-200'
}

function pickDay(date) {
  if (!date || isDisabledDay(date)) return
  if (pickerMode.value === 'date') {
    draftDate.value = date
    confirm()
    emit('close')
    return
  }
  if (!rangeStart.value || (rangeStart.value && rangeEnd.value)) {
    rangeStart.value = date
    rangeEnd.value = null
    return
  }
  if (dayDiff(rangeStart.value, date) >= 0) {
    rangeEnd.value = date
  } else {
    rangeStart.value = date
    rangeEnd.value = null
  }
}

function shiftViewMonth(delta) {
  const next = addMonths(viewYear.value, viewMonth.value, delta)
  if (isDisabledMonth(next.year, next.month)) return
  viewYear.value = next.year
  viewMonth.value = next.month
}

// 年份变化后把月份收敛到合法范围（上限年月 / 下限年月）
function clampMonth(year, month) {
  if (year === maxYear.value && month > maxMonth.value) return maxMonth.value
  if (year === minYear.value && month < minMonth.value) return minMonth.value
  return month
}

function applyYear(year) {
  if (pickerMode.value === 'month') {
    draftYear.value = year
    draftMonth.value = clampMonth(year, draftMonth.value)
  } else {
    viewYear.value = year
    viewMonth.value = clampMonth(year, viewMonth.value)
  }
}

function selectYear(event) {
  const year = Number(event.target.value)
  if (Number.isFinite(year) && year >= minYear.value && year <= maxYear.value) {
    applyYear(year)
  }
}

function shiftPanelYear(delta) {
  const target = shownYear.value + delta
  if (target > maxYear.value || target < minYear.value) return
  applyYear(target)
}

function pickMonth(month) {
  if (isDisabledMonth(shownYear.value, month)) return
  if (pickerMode.value === 'month') {
    draftMonth.value = month
    confirm()
    emit('close')
    return
  }
  viewMonth.value = month
  panel.value = 'calendar'
}

function applyPreset(key) {
  const now = todayDate()
  const end = isAfterDay(now, maxDay.value) ? maxDay.value : now

  if (pickerMode.value === 'month') {
    const target = key === 'lastMonth' ? addMonths(end.getFullYear(), end.getMonth() + 1, -1) : { year: end.getFullYear(), month: end.getMonth() + 1 }
    if (isDisabledMonth(target.year, target.month)) return
    draftYear.value = target.year
    draftMonth.value = target.month
    viewYear.value = target.year
    viewMonth.value = target.month
    confirm()
    emit('close')
    return
  }

  if (pickerMode.value === 'date') {
    draftDate.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
    confirm()
    emit('close')
    return
  }

  if (key === 'thisYear') {
    rangeStart.value = new Date(end.getFullYear(), 0, 1)
    rangeEnd.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  } else if (key === 'thisMonth') {
    rangeStart.value = startOfMonth(end.getFullYear(), end.getMonth() + 1)
    rangeEnd.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  } else if (key === 'lastMonth') {
    const prev = addMonths(end.getFullYear(), end.getMonth() + 1, -1)
    const lastDay = endOfMonth(prev.year, prev.month)
    rangeStart.value = startOfMonth(prev.year, prev.month)
    rangeEnd.value = isAfterDay(lastDay, maxDay.value) ? maxDay.value : lastDay
    viewYear.value = prev.year
    viewMonth.value = prev.month
  } else if (key === 'last7') {
    rangeStart.value = addDays(end, -6)
    rangeEnd.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  } else if (key === 'last30') {
    rangeStart.value = addDays(end, -29)
    rangeEnd.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  }
}

function resetDraft() {
  const now = todayDate()
  const end = isAfterDay(now, maxDay.value) ? maxDay.value : now
  if (pickerMode.value === 'month') {
    draftYear.value = end.getFullYear()
    draftMonth.value = end.getMonth() + 1
    viewYear.value = draftYear.value
    viewMonth.value = draftMonth.value
  } else if (pickerMode.value === 'date') {
    draftDate.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  } else {
    rangeStart.value = new Date(end.getFullYear(), 0, 1)
    rangeEnd.value = end
    viewYear.value = end.getFullYear()
    viewMonth.value = end.getMonth() + 1
  }
  panel.value = pickerMode.value === 'month' ? 'months' : 'calendar'
}

function confirm() {
  if (!canConfirm.value) return
  if (pickerMode.value === 'month') {
    emit('confirm', formatMonth(draftYear.value, draftMonth.value))
  } else if (pickerMode.value === 'date') {
    emit('confirm', formatDate(draftDate.value))
  } else {
    emit('confirm', { start: formatDate(rangeStart.value), end: formatDate(rangeEnd.value) })
  }
}
</script>

<template>
  <Transition name="dialog">
    <div
      v-if="open"
      class="fixed inset-0 z-[80] flex items-center justify-center bg-base-content/25 px-4 backdrop-blur-sm"
      @click.self="emit('close')"
    >
      <div
        class="dialog-card flex max-h-[85dvh] w-full max-w-sm flex-col overflow-hidden rounded-3xl bg-base-100 shadow-[0_16px_48px_rgba(40,70,110,0.24)]"
        role="dialog"
        aria-modal="true"
        :aria-label="pickerTitle"
      >
        <div class="border-b border-base-300/60 px-5 pb-4 pt-5">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-lg font-bold">{{ pickerTitle }}</p>
              <p class="mt-1 break-words text-sm leading-snug text-base-content/50">{{ summary }}</p>
            </div>
            <button
              type="button"
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-base-content/40 transition-colors active:bg-base-200"
              aria-label="关闭"
              @click="emit('close')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div v-if="showPresets && presets.length" class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="preset in presets"
              :key="preset.key"
              type="button"
              class="rounded-full bg-base-200/70 px-3 py-1.5 text-xs font-medium text-base-content/60 transition-colors active:bg-primary-soft active:text-primary"
              @click="applyPreset(preset.key)"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto px-4 pt-3" :class="pickerMode === 'range' ? 'pb-3' : 'pb-4'">
          <div v-if="pickerMode === 'month' || panel === 'months'">
            <div class="flex items-center justify-between">
              <button
                type="button"
                class="flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-30 disabled:active:bg-transparent"
                aria-label="上一年"
                :disabled="atMinPanelYear"
                @click="shiftPanelYear(-1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
                  <path d="m15 18-6-6 6-6" />
                </svg>
              </button>
              <label class="relative flex items-center">
                <select
                  :value="shownYear"
                  aria-label="选择年份"
                  class="h-8 appearance-none rounded-full bg-base-200/70 pl-3 pr-7 text-sm font-bold outline-none transition-colors active:bg-base-200"
                  @change="selectYear"
                >
                  <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
                </select>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="pointer-events-none absolute right-2 h-3 w-3 text-base-content/35">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </label>
              <button
                type="button"
                class="flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-30 disabled:active:bg-transparent"
                aria-label="下一年"
                :disabled="atMaxPanelYear"
                @click="shiftPanelYear(1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </button>
            </div>

            <div class="mt-3 grid grid-cols-3 gap-2">
              <button
                v-for="m in 12"
                :key="m"
                type="button"
                :disabled="isDisabledMonth(shownYear, m)"
                class="h-11 rounded-2xl text-sm font-medium transition-colors disabled:opacity-30"
                :class="
                  selectedPanelMonth === m
                    ? selectedPanelDisabled
                      ? 'bg-primary-soft text-primary/40'
                      : 'bg-primary text-primary-content'
                    : 'bg-base-200/60 text-base-content/70 active:bg-base-200'
                "
                @click="pickMonth(m)"
              >
                {{ m }}月
              </button>
            </div>
          </div>

          <div v-else>
            <div class="flex items-center justify-between">
              <button
                type="button"
                class="flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-30 disabled:active:bg-transparent"
                aria-label="上一个月"
                :disabled="atMinMonth"
                @click="shiftViewMonth(-1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
                  <path d="m15 18-6-6 6-6" />
                </svg>
              </button>
              <button
                type="button"
                class="flex items-center gap-1 text-sm font-bold transition-colors active:text-primary"
                aria-label="切换年月"
                @click="panel = 'months'"
              >
                {{ monthTitle }}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3 text-base-content/35">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>
              <button
                type="button"
                class="flex h-7 w-7 items-center justify-center rounded-full border border-base-300 text-base-content/50 transition-colors active:bg-base-200 disabled:opacity-30 disabled:active:bg-transparent"
                aria-label="下一个月"
                :disabled="atMaxMonth"
                @click="shiftViewMonth(1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5">
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </button>
            </div>

            <div class="mt-2 grid grid-cols-7 text-center text-[11px] text-base-content/40">
              <span v-for="w in WEEK_STARTS_MONDAY" :key="w" class="py-1">{{ w }}</span>
            </div>

            <div class="grid grid-cols-7 gap-y-1">
              <button
                v-for="(date, i) in cells"
                :key="i"
                type="button"
                :disabled="!date || isDisabledDay(date)"
                :aria-label="date ? formatDate(date) : undefined"
                class="flex h-10 items-center justify-center"
                @click="pickDay(date)"
              >
                <span
                  v-if="date"
                  class="relative flex h-8 w-8 items-center justify-center rounded-full text-sm transition-colors"
                  :class="dayClasses(date)"
                >
                  {{ date.getDate() }}
                  <span v-if="isTodayDay(date) && !isEndpoint(date)" class="absolute bottom-0.5 h-1 w-1 rounded-full bg-primary" />
                </span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="pickerMode === 'range'" class="flex items-center gap-3 border-t border-base-300/60 px-5 py-4">
          <button type="button" class="text-sm font-medium text-base-content/45 transition-colors active:text-base-content/70" @click="resetDraft">
            重置
          </button>
          <span class="flex-1" />
          <button
            type="button"
            class="h-10 w-20 rounded-2xl border border-base-300 text-sm font-semibold text-base-content/60 transition-transform active:scale-[0.98]"
            @click="emit('close')"
          >
            取消
          </button>
          <button
            type="button"
            class="h-10 w-20 rounded-2xl bg-primary text-sm font-semibold text-primary-content transition-transform active:scale-[0.98] disabled:opacity-40 disabled:active:scale-100"
            :disabled="!canConfirm"
            @click="confirm"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>
