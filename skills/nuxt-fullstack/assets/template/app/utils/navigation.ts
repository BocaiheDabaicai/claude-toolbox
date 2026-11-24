export type AdminNavIconName =
  | 'dashboard'
  | 'customers'
  | 'routes'
  | 'tasks'
  | 'employees'
  | 'teams'
  | 'settings'
  | 'clock'
  | 'menu'

interface AdminNavItem {
  to: string
  label: string
  icon: AdminNavIconName
  adminOnly?: boolean
}

interface AdminNavGroup {
  label: string
  items: AdminNavItem[]
}

/**
 * 后台导航配置：侧栏和顶栏面包屑共用。
 * 新增一级页面时在这里登记，再在侧栏图标组件里补一个图标。
 */
const ADMIN_NAV: AdminNavGroup[] = [
  {
    label: '业务',
    items: [
      { to: '/', label: '仪表盘', icon: 'dashboard' },
      { to: '/customers', label: '客户', icon: 'customers' },
    ],
  },
  {
    label: '系统',
    items: [{ to: '/settings', label: '设置', icon: 'settings' }],
  },
]

export function adminNavGroups(role?: string | null) {
  return ADMIN_NAV.map((group) => ({
    ...group,
    items: group.items.filter((item) => !item.adminOnly || role === 'admin'),
  })).filter((group) => group.items.length > 0)
}

export function findAdminNavLabel(path: string) {
  let match: AdminNavItem | undefined
  for (const group of ADMIN_NAV) {
    for (const item of group.items) {
      const hit =
        item.to === '/'
          ? path === '/'
          : path === item.to || path.startsWith(`${item.to}/`)
      if (hit && (!match || item.to.length > match.to.length)) match = item
    }
  }
  return match?.label ?? '管理后台'
}
