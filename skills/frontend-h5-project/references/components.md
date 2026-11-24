# 组件清单与用法

> `assets/template` 已包含「工程外壳 + 通用交互 + 日期选择」；商品、SKU、店铺等业务组件按项目实现，模式见 `patterns.md`。

## 1. 已包含在模板中的组件

| 组件 | 作用 | 关键接口 |
| --- | --- | --- |
| `layouts/DefaultLayout.vue` | H5 `max-w-md` 页面容器 + 路由过渡 | 读取 `meta.hideBottomNav` / `meta.fullHeight` |
| `layouts/AdminLayout.vue` | 管理台石墨侧栏 + 顶栏 + `max-w-7xl` | 内部导航数组、移动端抽屉、退出登录 |
| `layouts/PcLayout.vue` | PC 顶部导航 + 宽内容区 + 页脚 | 顶部导航数组 |
| `PageHeader.vue` | H5 二级页顶栏：返回 + 标题 + 首页 | `title`、`showHome`、`meta.backTo` |
| `AdminPageHeader.vue` | 后台页头：标题 + 描述 + 操作区 | `title`、`description`、`#actions` |
| `AdminNavIcon.vue` | 后台导航线性图标 | `name` |
| `BottomNav.vue` | 4 tab 悬浮底栏 | `activeName`、`badges` |
| `ToastHost.vue` | 全局轻提示挂载点 | 配合 `utils/toast.js` |
| `ConfirmDialog.vue` | 全局二次确认挂载点 | 配合 `utils/confirm.js` |
| `SkeletonBlock.vue` | 骨架块 | `rounded`、`tone` |
| `PaginationBar.vue` | 传统分页条；管理台自动收敛为小圆角 | `total`、`pageNum`、`pageSize`、`page-change`、`size-change` |
| `LoadMoreSentinel.vue` | 触底无限加载 | `disabled`、`@load` |
| `DatePickerDialog.vue` | 日期/年月/范围选择 | `open`、`mode`、`modelValue`、`minDate`、`maxDate`、`showPresets` |

### 1.1 PageHeader 与动态返回

`meta.backTo` 支持数组，用于「多个来源页都能正确返回」：

```js
{
  path: 'order/:orderId',
  name: 'orderDetail',
  meta: { hideBottomNav: true, backTo: 'orderList' },
},
{
  path: 'after-sale/:refundId',
  name: 'afterSaleDetail',
  meta: { hideBottomNav: true, backTo: ['orderList', 'orderDetail'] },
},
```

返回逻辑：

1. 上一页路径正好匹配某个 `backTo` 路由（支持 `:id` 动态段）→ `router.back()`；
2. 否则跳 `backTo` 第一项；
3. 没有 `backTo` 时优先历史返回，否则去首页。

修改路由的 `backTo` 时，同时检查 `PageHeader` 的动态路径匹配逻辑。

### 1.2 Toast / Confirm

```js
import { toast } from '@/utils/toast'
import { confirm } from '@/utils/confirm'

toast.success('已保存')
toast.error('保存失败')

if (await confirm({ title: '取消订单', message: '确定取消吗？', danger: true })) {
  // ...
}
```

- 二者都是 Promise / 全局单例，挂载点在 `App.vue`。
- 确认弹窗的 message 支持换行（`whitespace-pre-line`）。
- 请求层默认 toast，页面自渲染错误态时传 `silent: true`，避免重复提示。

### 1.3 分页

**上拉无限加载**（移动端首选）：`LoadMoreSentinel` 放在列表末尾。

```html
<LoadMoreSentinel v-if="hasMore" :disabled="loading" @load="loadList(false)" />
<p v-if="loading && list.length">正在加载...</p>
<p v-else-if="list.length && !hasMore">没有更多了</p>
```

**传统分页**（后台/流水类）：`PaginationBar`，监听 `page-change` / `size-change`。

加载函数要带请求令牌，避免快速切 tab 时旧响应覆盖新列表：

```js
let requestToken = 0
async function loadList(reset = true) {
  const token = ++requestToken
  // ...
  if (token !== requestToken) return
}
```

### 1.4 DatePickerDialog

```html
<DatePickerDialog
  v-model:open="pickerOpen"
  mode="date"
  :model-value="form.birthday"
  :min-date="'1900-01-01'"
  :max-date="today"
  :show-presets="false"
  @confirm="form.birthday = $event"
/>
```

- `mode`：`date` / `month` / `range`。
- 生日场景设置 `minDate`、年份下拉快速跳转，避免逐年翻页。
- 背景令牌使用 `primary-soft`，与其他弹层一致。

## 2. 业务组件模式（按项目实现）

| 组件 | 责任 | 关键点 |
| --- | --- | --- |
| `GoodsCard` | 商品卡 | 整图背景 + 深色渐变 + 白字；图片失败品牌渐变兜底；`aspect-[3/4]` |
| `GoodsCardSkeleton` | 商品卡骨架 | 与卡片同形，避免数据回来时跳变 |
| `ImageCarousel` | 商品图轮播 | 滑动、指示点、点击全屏；模糊原图铺底 + `object-contain` |
| `QuantityStepper` | 数量步进器 | 最小 1、库存封顶、点击输入框全选、手动输入校验 |
| `SkuPopup` | SKU 选择 | 规格组合可用性、库存、价格、加购/立即购买两种模式 |
| `StorePickerDialog` | 店铺切换 | 搜索、当前标记、距离、保存默认店铺后刷新页面数据 |
| `EmptyState` | 空态 | 图标 + 文案 + 主按钮；也可直接内联，避免过度抽象 |

### 2.1 图片状态

每个卡片/轮播单独维护 `loaded` / `failed`，不要用一个全局布尔。列表项用稳定 key（`goodsId + skuId`，分类用稳定分类 key），防止切换筛选时串图。

### 2.2 全屏预览

```html
<Teleport to="body">
  <Transition name="dialog">
    <div v-if="previewOpen" class="fixed inset-0 z-[90] bg-black" @click="close">
      <img class="absolute inset-0 h-full w-full scale-110 object-cover opacity-60 blur-2xl" />
      <img class="relative h-full w-full object-contain" />
    </div>
  </Transition>
</Teleport>
```

- 必须 `Teleport` 到 body，避免被 sticky 头图/信息卡的层叠上下文覆盖。
- 打开时锁定 `body.style.overflow = 'hidden'`，关闭恢复。
- 关闭按钮 `@click.stop`。

### 2.3 底部弹层

- 用 `sheet` 过渡（遮罩淡入 + 面板上滑）。
- 面板自身 `rounded-t-3xl`，内容区 `max-h-[70vh] overflow-y-auto`。
- 打开时锁定滚动；关闭点击遮罩。

## 3. 组件放置规则

- 全局单例（Toast / Confirm / 全屏预览）挂 `App.vue` 或 `Teleport`。
- 页面级弹层放页面内，不要提升为全局。
- 固定底栏放在页面过渡容器外。
- 通用组件不引入业务 store；需要业务数据时通过 props / events 传入。
- 组件命名用 PascalCase；页面以 `View` 结尾（`OrderListView.vue`）。

## 4. 新增组件检查清单

- [ ] props / emits 类型和默认值明确；
- [ ] 加载、空、错误、禁用状态齐全；
- [ ] 点击区域与 `@click.stop` 处理正确；
- [ ] 图片有加载/失败兜底；
- [ ] 固定定位处理 safe-area；
- [ ] `aria-label` 覆盖纯图标按钮；
- [ ] 在 `components.md` 或项目文档登记用途。
