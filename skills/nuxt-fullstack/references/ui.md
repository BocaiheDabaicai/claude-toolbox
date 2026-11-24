# UI 与设计系统

> 后台设计系统，不是 H5 主题。目标：简洁、清晰、严谨；信息密度高于会员端，装饰服从信息层级。
>
> 这套令牌同时用于 `frontend-h5-project` 的 Vue 管理台（`src/assets/styles/admin.css`）。修改后台颜色或结构时同步两处；H5 / PC 的消费者配色不在此列。

## 1. 与 H5 Skill 的关系

- 共享 Tailwind 4 + daisyUI 5 的技术方式、语义类命名和动效时长；
- **不共享配色**：H5 会员端保留「奶白 × 湖水蓝 × 薄荷绿」的消费者品牌色；后台使用本文件的「石墨侧栏 × 冷白内容 × 深湖蓝」方案；
- **不共享布局假设**：H5 是 `max-w-md` + 底部导航；后台是固定侧栏 + 顶栏 + 宽内容区；
- 同一工程同时包含 H5 与管理台时，用 `.admin-theme` 包住后台布局根节点，H5 继续使用自己的品牌令牌。

## 2. 颜色

令牌集中登记在 `app/assets/css/colors.css`，由 `app/assets/css/main.css` 的 `@theme` 映射为 Tailwind / daisyUI 语义变量。新增颜色只能改这两个文件，禁止在组件里写 `#xxxxxx`、`rgb()` 或渐变。

### 主色与中性色

| 令牌 | 值 | 用途 |
|---|---|---|
| `--brand-primary` | `#1F5FA8` | 主按钮、链接、选中态、关键数字 |
| `--brand-primary-soft` | `#EAF2FA` | 选中底、图标底、浅色标签 |
| `--brand-base-100` | `#FFFFFF` | 卡片、表格、顶栏 |
| `--brand-base-200` | `#F5F6F8` | 页面底 |
| `--brand-base-300` | `#E4E7EC` | 边框、分割线 |
| `--brand-base-content` | `#1D2939` | 正文与标题 |
| `--brand-secondary` | `#475467` | 次要按钮、中性标签 |

规则：

- 中性色承担约 90% 的界面；主色只用于主操作、选中态和链接，不要用来铺大面积背景；
- 正文对比度按 WCAG AA 起步，辅助文字至少 `text-base-content/60`；
- 语义色一律「深色文字 + 浅色底」；`admin.css` 已把 `badge-success` / `badge-warning` / `badge-error` 覆盖为浅底深字；
- 禁止：渐变 Logo、糖果色大色块、紫/粉装饰色、彩色投影。

### 深色侧栏

| 令牌 | 值 |
|---|---|
| `--admin-rail` | `#0F172A` |
| `--admin-rail-title` | `#F8FAFC` |
| `--admin-rail-link` | `rgba(255,255,255,.60)` |
| `--admin-rail-label` | `rgba(255,255,255,.45)` |
| `--admin-rail-active-bg` | `rgba(255,255,255,.06)` |
| `--admin-accent` | `#7CB3E8` |

侧栏结构样式由 `admin.css` 的 `.rail` / `.rail-border` / `.rail-title` / `.rail-subtitle` / `.rail-label` / `.rail-link` 提供，组件里不要重复写颜色。

## 3. 布局

### `app/layouts/default.vue`

- daisyUI `drawer lg:drawer-open`，根节点加 `admin-theme`；
- 桌面固定侧栏 `w-60`，石墨深色；
- 移动端顶栏菜单按钮 + 抽屉；
- 内容区 `max-w-7xl`，`p-4 lg:p-6`；
- 顶栏 `sticky top-0`，高度 `h-14`，白底 + 1px 下边框，不做大面积模糊/渐变。

### `app/layouts/auth.vue`

- 居中 `max-w-sm`；
- 纯色主色 Logo（8px 圆角），不使用渐变；
- 页面底 `bg-base-200`，登录卡片 1px 边框 + 轻微阴影。

### 侧栏导航

- 配置集中在 `app/utils/navigation.ts`，侧栏和顶栏面包屑共用；
- 分组显示：业务 / 管理 / 系统；组标题 11px、低对比度；
- 每项单行，高 36px，16px 线性图标，13px 文字；
- 选中态：`is-active` + 浅色背景 + 左侧 2px 高亮条；不要整块彩色胶囊；
- 移除每项的第二行描述，避免侧栏变成说明文档。

### 顶栏

- 左侧：移动端菜单按钮 + 面包屑「管理后台 / 当前页」；
- 右侧：姓名 + 角色 + 头像下拉；
- 不在顶栏重复应用名（侧栏已有品牌区）。

## 4. 组件

| 组件 / 类 | 用途 |
|---|---|
| `AppSidebar` | 石墨侧栏、分组导航、当前项高亮 |
| `AppTopbar` | 菜单按钮、面包屑、用户菜单 |
| `AppNavIcon` | 16px 线性图标，`currentColor` |
| `PageHeader` | 标题、描述、右侧操作 |
| `EmptyState` | 空态、说明、操作按钮 |
| `.panel` | 卡片、表格容器、设置分区 |

复杂表格/表单继续使用 daisyUI 类：`table`、`input input-bordered`、`select`、`textarea`、`modal modal-open`、`badge`、`btn`、`skeleton`、`loading`。

### 面板

```html
<div class="panel p-5">...</div>
<div class="panel overflow-hidden">...表格...</div>
```

- 1px 边框 + 8px 圆角 + 1px 级别阴影；
- 禁止 `rounded-2xl` / `shadow-xl` 的“大圆角 + 重投影”组合。

### 按钮

- 主操作：`btn btn-primary`；
- 次操作：`btn btn-outline`（已覆盖为细灰边框）；
- 表格内操作：`btn btn-ghost btn-xs`；删除加 `text-error`；
- 同一区域按钮高度保持一致，加载时禁用 + `loading loading-spinner loading-sm`。

### 状态标签

- 用 `badge badge-success` / `badge-warning` / `badge-error` / `badge-ghost`；
- 外观由 `admin.css` 统一为浅底深字 + 胶囊形；
- 禁止用高饱和实心色块承载长文本。

## 5. 页面状态

- 加载：`skeleton` 占位，不用整页 spinner；
- 空态：`EmptyState` + 明确下一步；
- 错误：可读文案 + 重试；
- 保存：按钮 loading + 禁用，防重复提交；
- 删除：二次确认，文案包含对象名称。

## 6. 表格

- 外层 `.panel overflow-hidden`，内部 `overflow-x-auto`；
- `admin.css` 已设置 `min-width: 680px`，窄屏横向滚动，不压缩列；
- 表头：12px、中等字重、浅灰底、`white-space: nowrap`；
- 行高：单元格上下 12px，行间 1px 浅色分隔；
- 行悬停：极浅灰底；
- 数字右对齐并使用 `tabular-nums`；
- 时间统一 `formatDateTime`；
- 操作列右对齐；分页显示“共 N 条”和当前页/总页数。

## 7. 仪表盘

- KPI 卡片只放业务指标（客户数、任务数、最近新增等），不要把数据库/认证等技术栈信息做成 KPI；
- 统计值用 `text-2xl font-semibold tabular-nums`；
- 指标卡右上角可放 32px 浅色图标块；
- 数量少时不要硬凑三张卡；两到三张业务卡 + 一张最近数据表即可。

## 8. 表单

- 标签在上，13px 中等字重；必填用 `*` 标记；
- 弹窗内表单 `grid sm:grid-cols-2`，`modal-box max-w-2xl`；
- 提交前客户端 Zod 校验，服务端再校验一次；
- 成功后关闭弹窗并刷新列表；
- 失败保留用户输入，错误放在表单底部，浅红底 + 深红字。

## 9. 响应式

至少检查：

- 320：单列、表格横向滚动、页头操作换行不溢出；
- 768：两列表单、侧边栏可抽屉；
- 1280：固定侧栏、宽内容区、表格完整展示。

## 10. 动效

- 页面切换使用 Nuxt `pageTransition` + `main.css` 的 `.page-*`；
- 时长 220ms，`cubic-bezier(0.25, 0.8, 0.35, 1)`；
- 尊重 `prefers-reduced-motion`；
- 不做影响可读性的装饰动画。

## 11. 日期与数字

```ts
formatDateTime(customer.createdAt)
```

- 固定 `Asia/Shanghai`，避免 SSR/客户端时区差异；
- 金额后续用 big.js/decimal，展示统一格式化；
- 统计数字使用 `tabular-nums`。

## 12. 改版检查清单

- [ ] 没有渐变 Logo、彩色投影、糖果色大面积背景；
- [ ] 卡片圆角 ≤ 8px，没有 `rounded-2xl` + `shadow-xl`；
- [ ] 主色只出现在主操作、选中态、链接和关键数字；
- [ ] 侧栏为单行分组导航，没有第二行描述；
- [ ] 顶栏没有重复应用名；
- [ ] 表格表头 12px + 浅灰底，窄屏可横向滚动；
- [ ] 状态标签为浅底深字；
- [ ] 仪表盘 KPI 是业务指标，不是技术栈信息；
- [ ] 正文辅助文字不低于 `text-base-content/60`；
- [ ] 新增颜色已登记在 `colors.css`。
