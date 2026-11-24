# __PROJECT_TITLE__

基于 Vue 3 + Vite 8 的 Web 项目骨架，覆盖 H5、管理后台、PC 三种界面形态。

## 技术栈

Vue 3.5 · Vite 8 · vue-router 5（hash）· Pinia 4 · Tailwind CSS 4 · daisyUI 5 · axios · big.js

## 快速开始

```bash
pnpm install
pnpm dev
pnpm build
```

环境要求：Node 20.19+ / 22.12+，pnpm 9.15.9。安装规则见 [AGENTS.md](AGENTS.md)。

## 三种界面形态

| 路由 | 形态 | 布局 |
| --- | --- | --- |
| `/` | H5 会员端 | `DefaultLayout` + 底部导航 |
| `/admin` | 管理后台 | `AdminLayout`（石墨侧栏 + 顶栏） |
| `/site` | PC 站点 | `PcLayout`（顶部导航 + 宽内容区） |

H5 / PC 使用 `src/assets/styles/colors.css` 的消费者品牌色；管理台使用 `src/assets/styles/admin.css` 的独立后台主题（石墨侧栏 + 冷白内容 + 深湖蓝）。从 `/admin` 跳到登录页时，登录卡片会自动切换为后台样式。

模板内置 DEV 演示登录；登录后可直接访问 `/admin`、`/site` 预览。接入真实后端后移除演示入口。

## 目录结构

```
src/
├─ api/          # 接口函数，按业务模块拆分
├─ assets/       # 图片与配色（colors.css / admin.css）
├─ components/   # 通用组件（AdminPageHeader / AdminNavIcon 等）
├─ layouts/      # DefaultLayout / AdminLayout / PcLayout
├─ router/       # 路由表与守卫
├─ stores/       # Pinia 状态
├─ utils/        # 请求、登录态、金额、日期、提示等
└─ views/        # 页面
   ├─ admin/     # 管理台页面
   └─ pc/        # PC 站点页面
```

## 接入步骤

1. 在 `.env.development` / `.env.production` 配置 `VITE_APP_BASE_API`。
2. 在 `src/utils/request.js` 按目标后端调整响应结构与请求头。
3. 在 `src/stores/user.js` 实现登录、用户信息与退出。
4. 在 `src/router/routes.js` 登记页面，在 `views/` 替换占位页。
5. 运行 `pnpm build`，确认 `pnpm-lock.yaml` 无非预期改动。

模板内的 DEV 演示登录只用于预览页面骨架，接入真实接口后请移除。
