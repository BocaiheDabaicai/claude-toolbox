# 管理后台 / PC 布局

> 同一套 Vue 3 工程，通过路由组选择布局。H5 / PC 共用消费者品牌色；管理台使用独立的「石墨侧栏 × 冷白内容 × 深湖蓝」后台主题。

## 1. 三种形态

| 形态 | 布局 | 路由组 | 容器 | 导航 | 配色 |
| --- | --- | --- | --- | --- | --- |
| H5 | `DefaultLayout` | `/` | `max-w-md` | 底部 4 tab | 消费者品牌色 |
| 管理台 | `AdminLayout` | `/admin` | `max-w-7xl` | 左侧栏 + 顶栏 | `.admin-theme` 后台主题 |
| PC | `PcLayout` | `/site` | `max-w-7xl` | 顶部导航 | 消费者品牌色 |

路由组父级统一加 `meta: { hideBottomNav: true }`，H5 底部导航不会出现在管理台 / PC。

## 2. 管理后台主题

### 2.1 令牌

管理台根节点加 `.admin-theme`，令牌集中在 `src/assets/styles/admin.css`，不修改 H5 的 `colors.css`。

| 令牌 | 值 | 用途 |
|---|---|---|
| `--color-primary` | `#1F5FA8` | 主按钮、链接、选中态 |
| `--color-primary-soft` | `#EAF2FA` | 选中底、图标底、浅色标签 |
| `--color-base-100` | `#FFFFFF` | 卡片、表格、顶栏 |
| `--color-base-200` | `#F5F6F8` | 页面底 |
| `--color-base-300` | `#E4E7EC` | 边框、分割线 |
| `--color-base-content` | `#1D2939` | 正文与标题 |
| `--color-secondary` | `#475467` | 次要按钮、中性标签 |

深色侧栏：

| 令牌 | 值 |
|---|---|
| `--admin-rail` | `#0F172A` |
| `--admin-rail-title` | `#F8FAFC` |
| `--admin-rail-link` | `rgba(255,255,255,.60)` |
| `--admin-rail-label` | `rgba(255,255,255,.45)` |
| `--admin-rail-active-bg` | `rgba(255,255,255,.06)` |
| `--admin-accent` | `#7CB3E8` |

规则：

- 中性色承担约 90% 的界面；主色只用于主操作、选中态和链接；
- 语义色一律「深色文字 + 浅色底」，用 `badge-success` / `badge-warning` / `badge-error` 表达状态；
- 圆角：卡片 8px、控件 6px、状态标签胶囊形；
- 禁止渐变 Logo、糖果色大面积背景、彩色投影、大圆角重投影。

> 这套令牌与 `nuxt-fullstack` 的后台主题保持一致。修改时同步两处，避免 Nuxt / Vue 模板分叉。

### 2.2 与 H5 / PC 的关系

- 字体、动效时长、基础组件（`Toast` / `Confirm` / `PaginationBar`）继续共用；
- H5 与 PC 继续使用 `colors.css` 的湖水蓝 / 薄荷绿品牌色；
- 管理台登录页也使用 `.admin-theme`：当从 `/admin` 跳到登录页时，`LoginView` 根据 `redirect` 自动切换为后台登录卡片。

## 3. 目录

```
src/
├─ assets/styles/
│  ├─ colors.css          # H5 / PC 消费者品牌色
│  └─ admin.css           # 管理后台主题与结构样式
├─ layouts/
│  ├─ DefaultLayout.vue   # H5：max-w-md + 路由过渡
│  ├─ AdminLayout.vue     # 管理台：石墨侧栏 + 顶栏 + 移动端抽屉
│  └─ PcLayout.vue        # PC：顶部导航 + 页脚
├─ components/
│  ├─ AdminPageHeader.vue # 后台页头：标题 + 描述 + 操作区
│  └─ AdminNavIcon.vue    # 后台导航线性图标
└─ views/
   ├─ admin/
   │  ├─ AdminDashboardView.vue
   │  └─ AdminCustomersView.vue
   └─ pc/
      └─ PcHomeView.vue
```

## 4. 路由登记

```js
{
  path: '/admin',
  component: () => import('@/layouts/AdminLayout.vue'),
  meta: { hideBottomNav: true },
  children: [
    {
      path: '',
      name: 'admin-home',
      component: () => import('@/views/admin/AdminDashboardView.vue'),
      meta: { title: '仪表盘' },
    },
    {
      path: 'customers',
      name: 'admin-customers',
      component: () => import('@/views/admin/AdminCustomersView.vue'),
      meta: { title: '客户管理' },
    },
  ],
},
{
  path: '/site',
  component: () => import('@/layouts/PcLayout.vue'),
  meta: { hideBottomNav: true },
  children: [
    {
      path: '',
      name: 'site-home',
      component: () => import('@/views/pc/PcHomeView.vue'),
      meta: { title: 'PC 首页' },
    },
  ],
},
```

- 管理台子路由的 `meta.title` 会显示在顶栏面包屑；
- 新增后台页 = 在 `/admin` 的 children 里登记 + 在 `src/views/admin` 建页面；
- 新增 PC 页 = 在 `/site` 的 children 里登记 + 在 `src/views/pc` 建页面；
- 登录回跳仍走 `safeRedirect`，`/admin`、`/site` 都是合法站内路径。

## 5. 管理台布局

`AdminLayout.vue`：

- 根节点 `admin-theme`；
- 桌面：`fixed w-60` 石墨侧栏 + `lg:pl-60` 内容区；
- 移动：侧边栏从左侧滑入，遮罩点击关闭；
- 侧栏品牌区 `h-14`，Logo 使用纯色主色（8px 圆角），不使用渐变；
- 导航按组显示（业务 / 系统），每项单行、36px 高、16px 图标、13px 文字；
- 选中态：浅色背景 + 左侧 2px `--admin-accent` 高亮条；
- 顶栏：`sticky top-0`、`h-14`，显示面包屑「管理后台 / 当前页」和用户；
- 内容：`max-w-7xl`，`p-4 lg:p-6`；
- 侧栏底部：返回 H5、退出登录；
- 路由变化自动关闭移动端侧边栏。

新增一级导航时，在 `AdminLayout.vue` 的 `navGroups` 登记 `{ name, to, label, icon }`，并在 `AdminNavIcon.vue` 补图标。

## 6. PC 布局

`PcLayout.vue`：

- 顶部 `sticky` 导航：品牌 + 页面链接 + 会员端入口；
- 内容 `max-w-7xl`；
- 底部页脚；
- 导航在 `md` 以下隐藏（可按项目加移动菜单）。

PC 页面以内容、营销、宽屏业务为主，不要照搬管理台的侧栏，也不要把后台的深色侧栏带到 PC 站点。

## 7. 表格页模式

`AdminCustomersView.vue` 是可复制的后台 CRUD 示例：

1. `AdminPageHeader`：标题、描述、右侧主操作（`btn btn-primary btn-sm`）；
2. 筛选区：`input input-bordered` + `select select-bordered` + 结果计数；
3. 表格容器：`panel overflow-hidden`；
4. 表格：`table` 类，窄屏由 `admin.css` 的 `min-width: 680px` 保证横向滚动；
5. 状态：`badge badge-success` / `badge badge-ghost`；
6. 空态：居中说明 + `btn btn-primary btn-sm`；
7. 分页：复用 `PaginationBar`，后台自动收敛为小圆角；
8. 新建/编辑：`dialog` 过渡 + `.panel` 弹窗；
9. 删除：`confirm({ danger: true })`；
10. 操作反馈：`toast.success/error`。

### 表格约定

- 外层 `overflow-x-auto`，窄屏横向滚动；
- 表头由 `admin.css` 统一为 12px、浅灰底、`white-space: nowrap`；
- 行高：单元格上下 12px，行间 1px 浅色分隔；
- 行悬停：极浅灰底；
- 操作列右对齐，编辑/删除用 `btn btn-ghost btn-xs`；
- 金额、数量用 `tabular-nums`。

## 8. 仪表盘

- KPI 卡片只放业务指标（订单、客户、待处理等），不要把数据库 / 认证等技术栈信息做成 KPI；
- 卡片使用 `.panel p-5`，右上角可放 32px 浅色图标块；
- 数量少时不要硬凑四张卡；两到三张业务卡 + 一张最近数据表即可；
- 图表、趋势后续接入真实数据后再加，示例数据要明确标注。

## 9. 表单 / 弹窗

- 弹窗最大宽度 `max-w-lg`，使用 `.panel`（8px 圆角、轻阴影）；
- 标签在上，13px 中等字重；必填用 `text-error` 标记；
- 输入框统一 `input input-bordered`，下拉 `select select-bordered`；
- 提交前在 `save()` 里做最小校验（如姓名必填）；
- 保存成功关闭弹窗，失败保留输入；
- 真实项目接 API 后，把本地数组替换为 `src/api` 请求，并保留 `silent` 错误处理约定。

## 10. 状态与交互

- 加载：表格骨架或行级 skeleton；
- 空态：说明 + 新建按钮；
- 错误：可读文案 + 重试；
- 删除：二次确认，文案含对象名称；
- 分页：筛选变化时重置到第 1 页；
- 不要用 `window.alert` 做业务提示，统一 `toast`。

## 11. 响应式检查

- 320：侧边栏隐藏、顶栏菜单可用、表格横向滚动；
- 768：筛选区横向排列，表格可读；
- 1280：侧边栏固定，内容区完整展开。

## 12. 新增页面清单

- [ ] 在对应路由组登记；
- [ ] 后台页面根节点位于 `admin-theme` 内；
- [ ] 页面使用 `AdminPageHeader`、`.panel`、`.table` 与 `PaginationBar`；
- [ ] 状态使用 `badge` 语义类，不写裸色值；
- [ ] 列表有加载 / 空 / 错误态；
- [ ] 操作有 Toast / Confirm；
- [ ] 320 / 768 / 1280 检查；
- [ ] `pnpm build` 通过；
- [ ] 更新 `docs/pages.md` 或 `docs/roadmap.md`。
