# AGENTS.md

## 项目环境（硬性要求）

本项目是 Nuxt 4 全栈业务应用，直接连接 PostgreSQL；依赖必须使用 pnpm 9 安装。

- Node.js：22.19+、24.11+ 或 26+
- pnpm：9.x，锁定 9.15.9（见 `package.json` 的 `packageManager`）
- 只在项目根目录执行 `pnpm install`
- 禁止 `npm install` / `yarn` / `bun install`，它们会生成第二套锁文件
- 禁止删除、重建或手工编辑 `pnpm-lock.yaml`
- 不要用 `--ignore-scripts` 绕过 `preinstall` 环境校验

## 常用命令

```bash
pnpm install
pnpm dev
pnpm build
pnpm typecheck
pnpm check              # 边界检查 + 类型检查
pnpm db:generate        # 由 schema 生成迁移
pnpm db:migrate         # 应用迁移
pnpm db:seed            # 创建管理员与示例数据
```

## 架构边界（必须遵守）

```
app/      客户端 + SSR 页面；不能 import 数据库
server/   API、数据库、会话、校验；服务端专属
shared/   Zod schema、类型；客户端与服务端共享
ops/      project.toml，供 opsctl 统一启停
```

- 数据库、Drizzle、pg、密码、会话密钥只能出现在 `server/`。
- `app/` 与 `shared/` 不能 import `drizzle-orm`、`pg`、`node:*` 或 `~~/server/*`。
- 页面通过 `/api/**` 访问数据，不直连数据库。
- 所有业务接口返回 `{ code, message, data }`；列表放在 `data: { rows, total, page, pageSize }`。
- 所有写接口必须在服务端用 Zod 校验，并做同源检查。
- 认证使用 HttpOnly Cookie 会话，不把 token 放 localStorage。
- 金额相关功能后续使用 big.js / decimal，不用浮点数直接计算。

## 状态管理

- 跨页面共享的客户端状态统一用 Pinia（`app/stores/*.ts`，选项式写法），与 `frontend-h5-project` 保持一致。
- 登录态在 `app/stores/auth.ts`；页面通过 `useAuth()` 兼容层访问，不要直接改 store state。
- 服务端数据用 `useApiFetch`（`useAsyncData` + `$fetch`/`useRequestFetch`），不要塞进 Pinia。
- 页面局部状态用 `ref` / `reactive`；不要新增全局 `useState`。

## UI 约定

- 后台主题为「石墨侧栏 × 冷白内容 × 深湖蓝」；颜色令牌在 `app/assets/css/colors.css`，结构样式在 `app/assets/css/admin.css`，布局根节点使用 `.admin-theme`。
- 颜色只用 `app/assets/css/main.css` 映射的语义类（`bg-primary`、`text-base-content/60` 等）。
- 新增色值先登记 `app/assets/css/colors.css`，禁止在组件里写裸色值、渐变或彩色投影。
- 卡片、表格容器、设置分区统一使用 `.panel`；禁止 `rounded-2xl` + `shadow-xl` 的组合。
- 状态标签使用 `badge` 语义类（`badge-success` 等），外观由 `admin.css` 统一为浅底深字。
- 导航在 `app/utils/navigation.ts` 登记，侧栏与顶栏面包屑共用；侧栏只放单行标签，不加第二行描述。
- 页面统一使用 `PageHeader`、`EmptyState` 与 daisyUI `card` / `table` / `modal` / `btn` 等组件类。
- 管理台以桌面优先、移动端可用为目标；H5 会员端另用 `frontend-h5-project`。
- 加载态使用 skeleton；空态使用 `EmptyState`；错误态显示可读信息。
- 日期统一走 `formatDateTime`，避免 SSR/客户端时区不一致导致 hydration mismatch。

## 数据库约定

- 每项目独立 database；表名复数、字段 snake_case。
- 必备审计字段：`created_at`、`updated_at`；需要软删时加 `deleted_at`。
- 主键使用 `bigserial`；索引按查询路径建，不盲目加。
- 迁移由 drizzle-kit 生成；已应用的迁移不改，只追加新迁移。
- 生产迁移由 `opsctl` 的 oneshot 服务执行，失败时阻止 Web 启动。

## 质量门禁

- `pnpm check` 通过；
- `pnpm build` 通过；
- `pnpm db:generate` 不产生意外 diff；
- `/api/healthz`、`/api/readyz` 正常；
- 登录、列表、创建、编辑、删除主链路验证通过；
- 320 / 768 / 1280 宽度下布局可用；
- `pnpm-lock.yaml` 无非预期改动。
