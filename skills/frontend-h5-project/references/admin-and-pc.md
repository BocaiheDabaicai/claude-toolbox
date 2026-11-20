# 管理后台 / PC 布局

> 同一套 Vue 3 工程，通过路由组选择布局；颜色、字体、动效和基础交互与 H5 共用。

## 1. 三种形态

| 形态 | 布局 | 路由组 | 容器 | 导航 |
| --- | --- | --- | --- | --- |
| H5 | `DefaultLayout` | `/` | `max-w-md` | 底部 4 tab |
| 管理台 | `AdminLayout` | `/admin` | `max-w-7xl` | 左侧栏 + 顶栏 |
| PC | `PcLayout` | `/site` | `max-w-7xl` | 顶部导航 |

路由组父级统一加 `meta: { hideBottomNav: true }`，H5 底部导航不会出现在管理台 / PC。

## 2. 目录

```
src/
├─ layouts/
│  ├─ DefaultLayout.vue    # H5：max-w-md + 路由过渡
│  ├─ AdminLayout.vue      # 管理台：侧边栏 + 顶栏 + 移动端抽屉
│  └─ PcLayout.vue         # PC：顶部导航 + 页脚
├─ components/
│  └─ AdminPageHeader.vue  # 后台页头：标题 + 描述 + 操作区
└─ views/
   ├─ admin/
   │  ├─ AdminDashboardView.vue
   │  └─ AdminCustomersView.vue
   └─ pc/
      └─ PcHomeView.vue
```

## 3. 路由登记

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

- 管理台子路由的 `meta.title` 会显示在顶栏；
- 新增后台页 = 在 `/admin` 的 children 里登记 + 在 `src/views/admin` 建页面；
- 新增 PC 页 = 在 `/site` 的 children 里登记 + 在 `src/views/pc` 建页面；
- 登录回跳仍走 `safeRedirect`，`/admin`、`/site` 都是合法站内路径。

## 4. 管理台布局

`AdminLayout.vue`：

- 桌面：`fixed w-64` 侧边栏 + `lg:pl-64` 内容区；
- 移动：侧边栏从左侧滑入，遮罩点击关闭；
- 顶栏：`sticky top-0`，显示当前页标题和用户；
- 内容：`max-w-7xl`，`p-4 lg:p-8`；
- 侧边栏底部：返回 H5、退出登录；
- 路由变化自动关闭移动端侧边栏。

新增一级导航时，在 `AdminLayout.vue` 的 `nav` 数组登记 `{ name, to, label, desc }`。

## 5. PC 布局

`PcLayout.vue`：

- 顶部 `sticky` 导航：品牌 + 页面链接 + 会员端入口；
- 内容 `max-w-7xl`；
- 底部页脚；
- 导航在 `md` 以下隐藏（可按项目加移动菜单）。

PC 页面以内容、营销、宽屏业务为主，不要照搬管理台的侧边栏。

## 6. 表格页模式

`AdminCustomersView.vue` 是可复制的后台 CRUD 示例：

1. `AdminPageHeader`：标题、描述、右侧主操作；
2. 筛选区：搜索输入 + 状态筛选 + 结果计数；
3. 表格卡片：`rounded-2xl border border-base-300 bg-base-100`；
4. 空态：居中说明 + 主操作；
5. 分页：复用 `PaginationBar`，监听 `page-change` / `size-change`；
6. 新建/编辑：`dialog` 过渡 + 居中弹窗；
7. 删除：`confirm({ danger: true })`；
8. 操作反馈：`toast.success/error`。

### 表格约定

- 外层 `overflow-x-auto`，窄屏横向滚动；
- 表头 `text-xs text-base-content/45`；
- 行 `hover:bg-base-200/50`；
- 状态用浅色底 + 对应功能色（`bg-success-soft text-success` 等）；
- 操作列右对齐，编辑/删除用文字按钮；
- 金额、数量用 `tabular-nums`。

## 7. 表单 / 弹窗

- 弹窗最大宽度 `max-w-lg`，`rounded-3xl`，使用现有 `dialog` 过渡；
- 标签在上，必填用 `text-error` 标记；
- 输入框统一 `h-10 rounded-xl border border-base-300`，聚焦 `focus:border-primary`；
- 提交前在 `save()` 里做最小校验（如姓名必填）；
- 保存成功关闭弹窗，失败保留输入；
- 真实项目接 API 后，把本地数组替换为 `src/api` 请求，并保留 `silent` 错误处理约定。

## 8. 状态与交互

- 加载：表格骨架或行级 skeleton；
- 空态：说明 + 新建按钮；
- 错误：可读文案 + 重试；
- 删除：二次确认，文案含对象名称；
- 分页：筛选变化时重置到第 1 页；
- 不要用 `window.alert` 做业务提示，统一 `toast`。

## 9. 响应式检查

- 320：侧边栏隐藏、顶栏菜单可用、表格横向滚动；
- 768：筛选区横向排列，表格可读；
- 1280：侧边栏固定，内容区完整展开。

## 10. 新增页面清单

- [ ] 在对应路由组登记；
- [ ] 页面使用 `AdminPageHeader` 或 PC 自己的标题区；
- [ ] 只使用语义色，不写裸色值；
- [ ] 列表有加载 / 空 / 错误态；
- [ ] 操作有 Toast / Confirm；
- [ ] 320 / 768 / 1280 检查；
- [ ] `pnpm build` 通过；
- [ ] 更新 `docs/pages.md` 或 `docs/roadmap.md`。
