# UI 与设计系统

## 1. 与 H5 Skill 的关系

- 共享 `colors.css` 品牌令牌与语义色；
- 共享 Tailwind 4 + daisyUI 5 的主题映射；
- 共享动效时长与缓动；
- **不共享布局假设**：H5 是 `max-w-md` + 底部导航；管理台是侧边栏 + 顶栏 + 宽内容区。

## 2. 颜色

只使用语义类：

```
bg-primary / text-primary
bg-primary-soft
bg-base-100 / bg-base-200 / bg-base-300
text-base-content / text-base-content/60
text-success / bg-error-soft / text-error
```

新增色值先登记 `app/assets/css/colors.css`，禁止在组件里写 `#xxxxxx` 或随意 `rgb()`。

## 3. 布局

`app/layouts/default.vue`：

- daisyUI `drawer lg:drawer-open`；
- 桌面固定侧边栏 `w-64`；
- 移动端顶栏菜单按钮 + 抽屉；
- 内容区 `max-w-7xl`，`p-4 lg:p-8`；
- 顶栏 sticky + 背景模糊。

`app/layouts/auth.vue`：

- 居中卡片、品牌渐变标识；
- 移动端安全边距。

## 4. 组件

| 组件 | 用途 |
|---|---|
| `AppSidebar` | 品牌、导航、当前项高亮 |
| `AppTopbar` | 菜单按钮、应用名、用户菜单 |
| `PageHeader` | 标题、描述、右侧操作 |
| `EmptyState` | 空态、说明、操作按钮 |

复杂表格/表单优先使用 daisyUI 类：`table`、`input input-bordered`、`select`、`textarea`、`modal modal-open`、`badge`、`btn`、`skeleton`、`loading`。

## 5. 页面状态

- 加载：`skeleton` 占位，不用整页 spinner；
- 空态：`EmptyState` + 明确下一步；
- 错误：可读文案 + 重试；
- 保存：按钮 loading + 禁用，防重复提交；
- 删除：二次确认，文案包含对象名称。

## 6. 表格

- 外层 `overflow-x-auto`；
- 表头简短，数字右对齐；
- 状态用 `badge`；
- 时间统一 `formatDateTime`；
- 操作列右对齐，次要操作 `btn-ghost btn-xs`；
- 分页显示“共 N 条”和当前页/总页数。

## 7. 表单

- 标签在上，错误靠近字段；
- 必填用 `*` 标记；
- 弹窗内表单 `grid sm:grid-cols-2`；
- 提交前客户端 Zod 校验，服务端再校验一次；
- 成功后关闭弹窗并刷新列表；
- 失败保留用户输入并显示服务端 message。

## 8. 响应式

至少检查：

- 320：单列、表格横向滚动、按钮不溢出；
- 768：两列表单、侧边栏可抽屉；
- 1280：固定侧边栏、宽内容区。

## 9. 动效

- 页面切换使用 Nuxt `pageTransition` + `main.css` 的 `.page-*`；
- 时长 220ms，`cubic-bezier(0.25, 0.8, 0.35, 1)`；
- 尊重 `prefers-reduced-motion`；
- 不做影响可读性的装饰动画。

## 10. 日期与数字

```ts
formatDateTime(customer.createdAt)
```

- 固定 `Asia/Shanghai`，避免 SSR/客户端时区差异；
- 金额后续用 big.js/decimal，展示统一格式化；
- 统计数字使用 `tabular-nums`。
