# 架构设计参考

> 目标：用同一套已验证的 Web 架构，快速生成新项目或迁移旧项目，覆盖 H5、管理后台、PC 三种形态。本文只写可复用的结构与决策，不绑定具体业务。

## 1. 设计原则

1. **只做 Web**：H5 / 管理台 / PC 三种形态；不引入 uni-app、HBuilderX、小程序条件编译。
2. **只迁在用页面**：置灰、注释、无入口、商户专用页面不迁（判定见 `pages.md` 模板）。
3. **不背旧包袱**：不复制旧全局 loading、Vuex、散落的 localStorage 读写、重复请求封装。
4. **接口契约为准**：不改后端；后端差异集中在请求层与 api 模块处理。
5. **形态匹配**：H5 用 `max-w-md` + 底栏；管理台用侧边栏；PC 用顶部导航；三者共用语义色、骨架屏和统一动效。
6. **文档先行**：先产出架构、接口、页面、路线图四份文档，再写页面。

## 2. 技术栈基线

| 类别 | 选型 | 版本 |
| --- | --- | --- |
| 框架 | Vue | `^3.5.41` |
| 构建 | Vite | `^8.2.2` |
| 路由 | vue-router（hash） | `^5.3.1` |
| 状态 | Pinia（选项式） | `^4.0.3` |
| 样式 | Tailwind CSS 4 + daisyUI 5 | `^4.3.3` / `^5.7.28` |
| 请求 | axios | `^1.20.0` |
| 金额 | big.js | `^7.0.1` |
| 字体 | @fontsource-variable/noto-sans-sc | `^5.3.1` |
| 包管理 | pnpm | `9.15.9` |
| Node | 20.19+ 或 22.12+ | Vite 8 要求 |

硬性约束：

- `packageManager` 锁定 `pnpm@9.15.9`，`.npmrc` 开启 `engine-strict=true`。
- 只允许 `pnpm install`；禁止 npm / yarn / bun；禁止删除或重建 `pnpm-lock.yaml`。
- `scripts/check-env.mjs` 在 `preinstall` 校验 pnpm 主版本、Node 版本、锁文件版本。
- 首次安装（锁文件不存在）只警告不拦截，方便新工程 bootstrap；之后强制校验 9.x。

## 3. 目录结构

```
src/
├─ api/            # 按业务模块拆文件：auth / user / goods / cart / order ...
├─ assets/
│  └─ styles/
│     └─ colors.css     # 品牌色唯一来源
├─ components/     # 通用组件：PageHeader / BottomNav / AdminPageHeader / ToastHost / ConfirmDialog ...
├─ layouts/        # DefaultLayout（H5）/ AdminLayout（后台）/ PcLayout（PC）
├─ router/
│  ├─ index.js     # createRouter + 守卫 + 滚动行为
│  ├─ routes.js    # 路由表（新增页面在此登记）
│  └─ legacy.js    # 旧 uni-app 路径 → 新路由映射
├─ stores/
│  ├─ index.js     # createPinia
│  ├─ user.js      # token / userInfo / login / logout
│  ├─ config.js    # merchantNo / storeId / storeInfo（按后端需要）
│  └─ cart.js      # 本地优先购物车（电商项目）
├─ utils/
│  ├─ request.js   # axios 实例 + 拦截器
│  ├─ auth.js      # token / userId 存取
│  ├─ toast.js / confirm.js / money.js / date.js / sanitize.js / sku.js
├─ views/          # 页面
│  ├─ admin/       # 管理台页面（仪表盘、客户管理等）
│  └─ pc/          # PC 站点页面
├─ App.vue         # router-view + BottomNav + ToastHost + ConfirmDialog
├─ main.js         # createApp().use(pinia).use(router)
└─ style.css       # Tailwind + daisyUI 主题映射 + 全局动效
```

## 4. 启动顺序

```js
// main.js：守卫依赖 store，必须先装 Pinia
createApp(App).use(pinia).use(router).mount('#app')
```

`App.vue` 负责三件全局的事：

1. `router-view` + `page` 过渡；
2. 登录后、非登录页、且未设置 `meta.hideBottomNav` 时挂载 `BottomNav`；
3. 全局挂载 `ToastHost` 与 `ConfirmDialog`。

首屏守卫拉取用户信息期间，用目标路由解析 `booting` 状态渲染底栏，避免刷新时底栏闪没。

### 4.1 三种布局的选择

| 形态 | 路由组 | 布局 | 容器 | 导航 |
| --- | --- | --- | --- | --- |
| H5 | `/` | `DefaultLayout` | `max-w-md` | 底部 4 tab |
| 管理台 | `/admin` | `AdminLayout` | `max-w-7xl` | 左侧栏 + 顶栏 |
| PC | `/site` | `PcLayout` | `max-w-7xl` | 顶部导航 |

- 管理台 / PC 路由组父级设置 `meta: { hideBottomNav: true }`，覆盖整组；
- 登录、请求层、Pinia、Toast、Confirm 全局共享；
- 布局细节与后台 CRUD 模式见 `admin-and-pc.md`。

## 5. 请求层

### 5.1 实例与拦截器

```js
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json;charset=utf-8' },
})
```

请求拦截统一注入：token（`Access-Token` 或 `Authorization: Bearer`）、商户/店铺、平台、UA 判断、经纬度等。页面不重复拼 header。

响应拦截统一处理：

| 情况 | 处理 |
| --- | --- |
| `code === 200` | 返回响应体，页面取 `data` |
| `code === 201` / 业务失败 | 默认 `toast.error(message)` 并 reject |
| `code === 1001` / HTTP 401 | 清 token、跳登录、提示过期 |
| `status === 5000`（部分后端） | 按错误处理 |
| 页面要自渲染错误态 | 请求配置传 `silent: true` |

### 5.2 兼容不同后端

- **fuint clientApi**：`{ code, message, data }`，业务失败常用 `201`。
- **RuoYi**：`{ code, msg, rows, total }` 或 `{ code, msg, data }`，`401` 表示未登录。
- 其他结构在拦截器里集中适配；api 模块保持薄封装。

### 5.3 分页归一化

后端常见两种分页：`{ content, totalElements, totalPages }` 与 `{ list, total }`，偶发 `data.data.content`。在 api 层或页面加载函数里统一成一种结构，避免每个页面各写一套。

## 6. 登录态与用户信息

```js
// stores/user.js（选项式）
state: () => ({ token: getToken(), userInfo: null })
getters: { isLoggedIn: (state) => !!state.token }
actions:
  - login(data)      // 调登录接口 → 写 token → getInfo()
  - getInfo()        // 拉 userInfo，失败时 reset
  - logout()         // 服务端失败也清本地
  - reset()          // 清 token / userInfo / userId / 其他 store
```

约定：

- token 持久化到 localStorage，key 带项目前缀（如 `myapp_token`）。
- `userInfo` 只在内存；刷新后由路由守卫重新拉取。
- 当前用户 ID 写入 `utils/auth.js` 的 `getUserId()`，需要会员归属的接口从这里取，禁止由调用方随意传入。
- 退出登录要同时清空依赖登录态的 store（购物车、筛选、渠道等）。

## 7. 登录前初始化（重要模式）

部分后端要求登录接口携带非 0 的 `storeId` / `merchantNo`，而登录页本身没有店铺来源。用 config store 解决：

```js
// stores/config.js
state: () => ({
  merchantNo: getMerchantNo(),
  storeId: getStoreId(),
  storeInfo: getStoreInfo(),
  initialized: false,
})
getters: { hasStore: (state) => state.storeId > 0 }
actions:
  - async ensureInitialized() {
      if (this.storeId > 0) return this.storeInfo
      // 并发去重：模块级 initPromise
      const res = await getSystemConfig({ silent: true })
      this.applySystemConfig(res.data)
    }
```

路由守卫在任何页面进入前先 `await configStore.ensureInitialized().catch(() => {})`，登录页也不例外。这是旧项目最常见的隐性坑，不要依赖用户先进首页。

## 8. 路由

- **hash 模式**：`createWebHashHistory()`，部署无需服务端 rewrite。
- **滚动行为**：`return savedPosition || { top: 0 }`。
- **meta 约定**：

| meta | 作用 |
| --- | --- |
| `hideBottomNav` | 二级页隐藏底栏 |
| `backTo` | 顶栏返回的上级路由名；数组表示多个合法上级 |
| `fullHeight` | 页面自行管理底部留白（固定高度双栏布局） |
| `title` | 占位页/模板文档使用 |

守卫顺序：

1. 初始化店铺/商户（如需要）；
2. 未登录 → 仅允许 `login`，其余跳登录并带 `redirect`；
3. 已登录但 `userInfo` 为空 → `getInfo()`；失败清态回登录；
4. 已登录访问 `login` → 跳首页。

旧路径映射集中在 `router/legacy.js`：banner、navigation、文章链接、旧分享路径都可能指向 `pages/xxx`，不要散落在页面里判断。

## 9. 状态管理

- 统一 Pinia 选项式写法，便于阅读和迁移。
- 只把跨页/跨刷新需要的内容放 store；列表、分页、表单留在页面内。
- 持久化策略写清楚：token 持久化；userInfo 不持久化；config 的 merchantNo/storeId 持久化。
- 购物车、筛选等高频状态如需本地优先，建独立 store，不要在页面里直接读写 localStorage。

## 10. 布局与全局挂载

- `DefaultLayout`：`mx-auto min-h-screen w-full max-w-md bg-base-100`，桌面端加左右边框和阴影。
- 底部导航固定在视口底部，页面容器根据 `hideBottomNav` / `fullHeight` 预留 `pb-28` / `pb-6` / `pb-0`。
- 全局弹层（Toast、Confirm）挂在 `App.vue`；全屏预览用 `Teleport to="body"`。
- 固定底栏放在页面过渡容器之外，避免父级 `transform` 影响 `position: fixed`。

## 11. 环境与部署

```
# .env.development / .env.production
VITE_APP_BASE_API=https://...
VITE_APP_TITLE=...
```

- 构建产物为纯静态文件，直接放 nginx；hash 路由无需 rewrite。
- 图片等静态资源通常由接口返回绝对地址，不需要单独代理。
- 测试服证书若只覆盖域名不覆盖 IP，团队应统一使用域名，避免每台机器手动加例外。

## 12. 反模式

- 全局 loading / 全局 Vuex / Vue2 mixin / HBuilderX 依赖。
- 页面各自拼 header、各自判断 `code`、各自弹错误。
- 直接 `v-html` 后端富文本（必须先白名单清洗）。
- 用浮点数直接算金额（统一 `big.js`）。
- 在页面里散落 `localStorage` key（统一走 utils/store）。
- 为“能装上”而删除锁文件或改用 npm/yarn。

## 13. 新项目检查清单

- [ ] `pnpm install` 成功，锁文件 `lockfileVersion: '9.x'`；
- [ ] `pnpm dev` 可启动，4 tab 正常切换；
- [ ] `meta.hideBottomNav` / `backTo` 生效；
- [ ] 请求头在 Network 中可见 token / 商户 / 店铺；
- [ ] 清空 localStorage 后登录链路可走通；
- [ ] `pnpm build` 通过，锁文件无漂移。
