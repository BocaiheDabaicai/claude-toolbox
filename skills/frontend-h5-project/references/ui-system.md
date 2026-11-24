# UI 设计系统

> 本文件是 **H5 会员端 / PC 站点**的消费者视觉规范，风格关键词：奶白、湖水蓝、薄荷绿；清新、健康、自然、干净。
> 目标：同一套视觉语言可以复用到会员商城、返利、收银 H5 等移动端项目。

> **管理后台不使用这套配色。** 后台有独立的「石墨侧栏 × 冷白内容 × 深湖蓝」主题，令牌与实现见 `src/assets/styles/admin.css` 与 `admin-and-pc.md`。两套主题共享字体、动效和基础组件，但不共享颜色。

## 1. 颜色：唯一来源

所有颜色登记在 `src/assets/styles/colors.css`，组件只使用语义类或 `var(--brand-*)`，禁止随意写色值。

### 1.1 品牌色

| 变量 | 参考值 | 用途 |
| --- | --- | --- |
| `--brand-primary` | `oklch(60% 0.1 235)` ≈ `#4E96D6` | 按钮、链接、选中态、重点区域 |
| `--brand-primary-content` | 近白 | 主色上的文字 |
| `--brand-secondary` | `oklch(78% 0.1 180)` ≈ `#7ED8BB` | 渐变搭档、健康自然标识 |
| `--brand-secondary-content` | 深绿 | 次色上的文字 |
| `--brand-accent` | `oklch(50% 0.09 250)` ≈ `#2E6EAD` | 价格、金额、重要数字 |
| `--brand-accent-content` | 近白 | 强调色上的文字 |

### 1.2 底色与文字

| 变量 | 参考值 | 用途 |
| --- | --- | --- |
| `--brand-base-100` | 纯白 | 卡片、弹层 |
| `--brand-base-200` | 奶蓝白 ≈ `#F6FAFD` | 页面底 |
| `--brand-base-300` | 浅蓝灰 ≈ `#E4EDF5` | 边框、分割线 |
| `--brand-base-content` | 深蓝灰 ≈ `#2A3B57` | 正文文字 |

### 1.3 功能色与浅色底

| 变量 | 用途 |
| --- | --- |
| `--brand-info` / `--brand-success` / `--brand-warning` / `--brand-error` | 状态、提示 |
| `--brand-primary-soft` | 浅蓝底：选中态、标签、提示块 |
| `--brand-success-soft` / `--brand-warning-soft` / `--brand-error-soft` | 对应状态浅底 |

> 为什么要有 `*-soft`：Tailwind 的 `bg-primary/10` 依赖 `color-mix`，部分浏览器会退化成实色，导致同色文字不可见。浅色底必须用预定义的 soft 变量。

### 1.4 渐变

```css
--brand-gradient: linear-gradient(135deg, #5fa8ec 0%, #6cc7a8 100%);
--brand-gradient-air: linear-gradient(135deg, #e8f4fe 0%, #ffffff 50%, #e9f9f2 100%);
```

- `--brand-gradient`：登录头图、会员卡片、重点强调块。
- `--brand-gradient-air`：图片加载占位、空气感分区底。

### 1.5 语义映射

`src/style.css` 用 `@theme` 把品牌变量映射为 Tailwind / daisyUI 语义变量：

```css
@import "tailwindcss";
@import "./assets/styles/colors.css";
@plugin "daisyui" { themes: false; }

@theme {
  --color-primary: var(--brand-primary);
  --color-primary-content: var(--brand-primary-content);
  --color-primary-soft: var(--brand-primary-soft);
  /* secondary / accent / base-* / info / success / warning / error 同理 */
  --radius-selector: 1rem;
  --radius-field: 0.5rem;
  --radius-box: 1rem;
}
```

关闭 daisyUI 内置主题很重要：默认主题会用自己的主色覆盖品牌色。

## 2. 字体

```css
--font-sans:
  -apple-system, BlinkMacSystemFont, 'PingFang SC',
  'Noto Sans SC Variable', 'Microsoft YaHei', sans-serif;
```

- Apple 设备命中系统苹方；其他平台使用打包的 Noto Sans SC。
- 引入 `@fontsource-variable/noto-sans-sc` 后，构建产物包含 101 个 `unicode-range` 切片，浏览器只下载当前页面用到的切片。
- 全局 `font-variant-numeric: tabular-nums`，价格、数量、订单号等数字列对齐。
- `-webkit-font-smoothing: antialiased`，深色文字在浅底上更干净。

## 3. 布局

### 3.1 H5 会员端

- 全站 `max-w-md`（约 448px）居中；桌面端加 `sm:border-x` 与柔和阴影。
- 页面底 `bg-base-200`，卡片 `bg-base-100`。
- 顶栏 `sticky top-0`，半透明 + `backdrop-blur`。
- 底部导航固定，容器预留 `pb-[calc(env(safe-area-inset-bottom)+0.75rem)]`。
- 所有固定底栏都要加 `env(safe-area-inset-bottom)`，iPhone 才不会压到 home indicator。

### 3.2 管理后台 / PC

- **PC 站点**与 H5 共用本文件的消费者品牌色、字体和动效；顶部导航 + 宽内容区 + 页脚；`md` 以下隐藏桌面导航。
- **管理台**使用独立的 `.admin-theme` 后台主题：
  - 石墨侧栏 `w-60` + 顶栏 `h-14` + 内容 `max-w-7xl`、`p-4 lg:p-6`；
  - 页面底 `#F5F6F8`，面板 `.panel`（白底、1px 边框、8px 圆角、轻阴影）；
  - 表格 `.table` 由 `admin.css` 统一表头、行高和横向滚动；
  - 状态用 `badge` 语义类，浅底深字。
- 三种形态共用请求层、登录态、字体和动效；**不要**把 H5 的奶白 / 薄荷绿硬套到管理台，也不要给 PC 站点加后台深色侧栏。
- 详细模式见 `admin-and-pc.md`。

#### 3.3 卡片与阴影（H5 / PC）

- 内容区卡片常用 `rounded-2xl` / `rounded-3xl`，阴影克制：

```
shadow-[0_2px_10px_rgba(42,59,87,0.04)]   # 普通卡片
shadow-[0_8px_24px_rgba(42,59,87,0.12)]   # 浮层/状态头
shadow-[0_6px_18px_rgba(78,150,214,0.28)] # 主按钮
```

## 4. 动效

```css
:root {
  --motion-fast: 150ms;      /* 颜色、透明度 */
  --motion-expand: 200ms;    /* 展开、弹层 */
  --motion-page: 220ms;      /* 页面切换 */
  --motion-swap: 220ms;      /* 骨架屏 → 内容 */
  --motion-carousel: 500ms;  /* 轮播、图片 */
  --motion-ease: cubic-bezier(0.25, 0.8, 0.35, 1);
}
```

| 过渡名 | 行为 | 用途 |
| --- | --- | --- |
| `page` | 新页面淡入 + 上移 8px | 路由切换 |
| `swap` | 旧内容 100ms 淡出，新内容 220ms 上浮淡入 | 骨架屏 → 内容、列表状态切换 |
| `list-item` | 卡片错峰淡入上移，`--stagger` 控制延迟 | 列表入场 |
| `toast` | 顶部滑入、原地叠放 | 轻提示 |
| `dialog` | 遮罩淡入 + 卡片缩放 0.96→1 | 确认弹窗 |
| `sheet` | 遮罩淡入 + 底部面板上滑 | 底部筛选面板 |

规则：

- 骨架屏与内容不要 `v-if` 硬切换，用 `swap`。
- 固定底栏放在过渡容器外，避免父级 `transform` 影响 `position: fixed`。
- 尊重 `prefers-reduced-motion: reduce`，统一关闭装饰动画。
- 点击反馈用 `active:scale-[0.98]` / `active:bg-base-200`，时长即时。

## 5. 图片加载

统一模式：**渐变占位 → 图片 500ms 淡入 → 失败回落到渐变/首字**。

```html
<div class="relative overflow-hidden rounded-2xl">
  <div class="absolute inset-0 bg-gradient-to-br from-primary via-accent to-secondary" />
  <img
    v-if="src && !failed"
    :src="src"
    loading="lazy"
    class="absolute inset-0 h-full w-full object-cover transition-opacity duration-500"
    :class="loaded ? 'opacity-100' : 'opacity-0'"
    @load="loaded = true"
    @error="failed = true"
  />
</div>
```

- 商品卡/购物车缩略图：品牌渐变兜底。
- 分类图标：无图/失败显示名称首字。
- 轮播 banner：品牌浅渐变占位；图片 `object-contain` + 同图模糊背景铺底；后台无图/失败可用本地备用图。
- 不要在图片未加载时用纯灰块长时间停留；渐变占位更接近最终视觉。

## 6. 加载 / 空 / 错误态

| 状态 | 做法 |
| --- | --- |
| 页面首次加载 | 与最终布局同形的骨架屏（`SkeletonBlock` / 卡片骨架） |
| 列表加载更多 | 底部 `LoadMoreSentinel` + “正在加载...” |
| 空列表 | 居中图标 + 一句说明 + 主按钮（如“去逛逛”） |
| 请求失败 | 居中错误图标 + 文案 + “重新加载”按钮；请求用 `silent` 避免重复 toast |
| 按钮提交中 | 文案切换 + `disabled`，不要复用全局 loading |

## 7. 组件视觉规则（H5 / PC）

> 管理台组件规则见 `admin-and-pc.md`：`.panel`、`.table`、`badge`、`AdminPageHeader`、`AdminNavIcon`。

- **PageHeader**：高 48px，左返回，中间标题，右侧首页图标；返回逻辑见组件文档。
- **BottomNav**：悬浮圆角条，4 个 tab；选中态 `bg-primary-soft text-primary`；角标用 `bg-error`。
- **卡片**：白底、`rounded-2xl`、内边距 16px、极轻阴影；不要用重边框。
- **主按钮**：`h-11 rounded-full bg-primary text-primary-content`，带柔和主色阴影。
- **次按钮**：白底 + `border-base-300`；危险操作 `text-error` + `border-error/35`。
- **标签/状态**：`rounded-full px-2 py-0.5 text-[10px] font-semibold`，用 soft 背景 + 对应文字色。
- **列表行**：左图右文，名称最多两行，价格用 `text-accent`，数量右对齐。
- **弹层**：`ConfirmDialog` 最大 `max-w-xs`、`rounded-3xl`；底部面板用 `sheet` 过渡。

## 8. 可访问性与移动端细节

- 图标按钮必须有 `aria-label`。
- 可点击区域至少 36–44px；列表整卡可点时，内部按钮要 `@click.stop`。
- 输入框使用 `inputmode` / `autocomplete`，数字输入点击时全选。
- 横向滚动容器加 `overscroll-contain` 和隐藏滚动条样式（`no-scrollbar`）。
- 图片 `draggable="false"`，避免长按拖拽。
- 全屏预览/弹层打开时锁定 `body` 滚动，关闭后恢复。

## 9. Do / Don't

**Do**

- 先用语义类，再考虑自定义样式。
- 新增颜色先登记 `colors.css`。
- 异步内容用骨架屏和 `swap`。
- 金额统一 `formatAmount`，时间统一 `formatDateTime`。
- 空态、错误态、加载态一起设计。

**Don't**

- 不要在组件里写死 `#4E96D6` 之类的色值。
- 不要把 H5 的湖水蓝 / 薄荷绿硬套到管理台；后台使用 `.admin-theme` 令牌。
- 不要用 `bg-primary/10` 做浅色底（用 `primary-soft`）。
- 不要让骨架屏与内容直接硬切。
- 不要把 `position: fixed` 的底栏放进有 `transform` 的过渡容器。
- 不要直接 `v-html` 后端富文本。
- 不要给后台加渐变 Logo、糖果色大色块、彩色投影或 `rounded-2xl + shadow-xl`。
