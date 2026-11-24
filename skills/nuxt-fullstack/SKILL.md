---
name: nuxt-fullstack
description: 当用户要求“新建 Nuxt 全栈业务应用”“Nuxt 直连 PostgreSQL”“快速做管理后台/内部系统”“生成 Nuxt + Drizzle 项目骨架”“做一套区别于 H5 的专业后台 UI”，或需要一个可复用的 Nuxt 4 + PostgreSQL + Cookie 会话 + Tailwind/daisyUI 业务模板时使用。覆盖服务端/客户端边界、Drizzle 迁移、认证、CRUD 模式、健康检查、opsctl 运维清单和质量门禁；不覆盖多节点部署、微服务、复杂工作流引擎。
version: 0.2.0
---

# Nuxt 全栈业务应用

## 目标

用一套经过构建验证的 Nuxt 4 架构，快速生成“页面 + API + PostgreSQL”一体的业务应用。适合管理后台、内部系统和需要快速迭代的业务闭环；生产环境由 systemd/opsctl 托管。

## 何时使用

- 新建 Nuxt 4 业务应用，需要直接连接 PostgreSQL；
- 快速做管理后台、内部工具、MVP；
- 需要 Cookie 会话、Drizzle 迁移、统一 API 响应和 CRUD 骨架；
- 需要一套与会员端 H5 区分开的后台视觉：石墨侧栏、冷白内容区、深湖蓝主色；
- 需要统一的表格、表单、状态标签和空态模式；
- 需要一个自带 `ops/project.toml`、能被 `opsctl` 统一启停的项目。

## 何时不用

- 前后端分离、需要独立扩展后端 → 用 Vue H5 + FastAPI；
- 纯移动端会员 H5 → 用 `frontend-h5-project`；
- 多节点、微服务、服务网格 → 不在本 Skill 范围；
- 复杂工作流、规则引擎、强事务金融核心 → 需要单独评估。

## 技术基线

| 类别 | 选型 | 版本 |
|---|---|---|
| 框架 | Nuxt | 4.5.2 |
| 运行时 | Node.js | 22.19+ / 24.11+ / 26+ |
| 包管理 | pnpm | 9.15.9 |
| 数据库 | PostgreSQL | 当前稳定版 |
| ORM / 迁移 | Drizzle ORM / drizzle-kit | 0.45.4 / 0.31.11 |
| 样式 | Tailwind CSS + daisyUI | 4.3.5 / 5.7.28 |
| 校验 | Zod | 4.6.7 |
| 语言 | TypeScript | 5.9.3 |

> daisyUI 固定在 5.7.28：5.8.x 在 Nuxt 4.5 / Vite 7 下会产生 CSS 解析警告。

## 架构

```
app/          页面、布局、组件、composable、样式（客户端 + SSR）
server/       API、数据库、会话、密码、校验（仅服务端）
shared/       Zod schema、API/业务类型（客户端与服务端共享）
ops/          project.toml，供 opsctl 统一启停
docs/         brief / features / data-model / decisions / roadmap
```

请求链路：

```
浏览器 → Nuxt 页面 / SSR → /api/** → Drizzle → PostgreSQL
                │
                └── Cookie 会话（HttpOnly）
```

## 标准工作流

### 0. 确认输入

- 项目 slug（小写字母/数字/中划线）与显示名称；
- 数据库名（建议 `app_<slug>`）；
- 管理员邮箱与初始密码；
- 部署目录与端口（默认 3000）；
- 是否已有 PostgreSQL 与 Node 22.19+。

### 1. 生成项目

```bash
node .claude/skills/nuxt-fullstack/scripts/scaffold.mjs ../my-admin \
  --name my-admin \
  --title "我的管理台"
```

脚本会复制模板、替换占位符、生成 `docs/` 和带随机 `NUXT_SESSION_SECRET` 的 `.env`。

### 2. 文档先行

填写：

- `docs/brief.md`：背景、目标、范围、约束；
- `docs/features.md`：功能点台账与验收标准；
- `docs/data-model.md`：表、字段、索引、迁移；
- `docs/decisions.md`：关键决策与代价；
- `docs/roadmap.md`：阶段、下一次开工步骤。

### 3. 环境与数据库

```bash
cd ../my-admin
# 修改 .env：NUXT_DATABASE_URL、SEED_ADMIN_EMAIL、SEED_ADMIN_PASSWORD
pnpm install
pnpm db:generate
pnpm db:migrate
pnpm db:seed
pnpm dev
```

### 4. 按垂直切片开发

1. 登录 + 会话；
2. 仪表盘；
3. 第一个业务域的列表/创建/编辑/删除；
4. 搜索、分页、状态；
5. 下一个业务域。

每个切片都走完：`shared/schema` → `server/database/schema` → `server/api` → `app/pages` → `pnpm check`。

### 5. 质量门禁

```bash
pnpm check
pnpm build
pnpm db:generate   # 应无 schema 变更
```

### 6. 运维接入

确认 `ops/project.toml` 与端口、健康路径一致，然后：

```bash
opsctl doctor --root /srv/projects
opsctl install my-admin --root /srv/projects
opsctl install my-admin --root /srv/projects --apply
opsctl status my-admin --root /srv/projects
```

## 硬性规则

- 数据库、`drizzle-orm`、`pg`、`node:*`、会话/密码逻辑只能出现在 `server/`。
- `app/` 与 `shared/` 不得引用 `server/`；`pnpm check:boundary` 必须通过。
- 所有业务接口返回 `{ code, message, data }`；列表统一 `data: { rows, total, page, pageSize }`。
- 所有写接口用 Zod 校验，并做同源检查（`requireSameOrigin`）。
- 认证使用 HttpOnly Cookie 会话，不把 token 放 localStorage。
- 颜色只用语义类；后台令牌登记 `app/assets/css/colors.css`，结构样式放 `app/assets/css/admin.css`；禁止渐变、糖果色和组件内裸色值。
- 迁移由 drizzle-kit 生成；已应用的迁移不改，只追加。
- 每个项目必须提供 `ops/project.toml`、`/api/healthz`、`/api/readyz`。
- 只用 pnpm 9；禁止 npm/yarn/bun，禁止删除或重写 `pnpm-lock.yaml`。
- 密钥只放 `.env`，服务器上 `chmod 600`；仓库里只提交 `.env.example`。

## 质量门禁

- `pnpm check` 通过（边界 + 类型）；
- `pnpm build` 通过；
- `pnpm db:generate` 无意外 diff；
- `/api/healthz` 返回 200，`/api/readyz` 在数据库可用时返回 200；
- 登录、列表、创建、编辑、删除主链路验证；
- 320 / 768 / 1280 宽度布局正常；
- 浏览器控制台无 error；
- `opsctl status` 显示 healthy；
- `docs/roadmap.md` 已更新。

## 资源索引

### references（按需加载）

- `references/architecture.md`：Nuxt 4 目录、SSR、API 边界、响应结构、错误处理。
- `references/database.md`：PostgreSQL 约定、Drizzle schema/迁移、索引、软删、连接池。
- `references/auth.md`：Cookie 会话、scrypt、同源检查、角色与安全清单。
- `references/ui.md`：后台设计令牌、石墨侧栏、分组导航、面板/表格/表单/状态标签、空态与响应式规范。
- `references/patterns.md`：垂直切片、列表搜索分页、CRUD、软删、错误处理。
- `references/ops.md`：project.toml、迁移 oneshot、构建/启动、systemd、部署顺序。
- `references/quality.md`：检查命令、测试策略、回归与安全清单。

### assets

- `assets/template/`：可运行的 Nuxt 4 模板（登录、仪表盘、客户 CRUD、Drizzle 迁移、ops manifest）。
- `assets/docs-templates/`：brief / features / data-model / decisions / roadmap。

### scripts

- `scripts/scaffold.mjs`：复制模板、替换占位符、生成 docs 与 `.env`。

## 与其他 Skill 的关系

- `frontend-h5-project`：移动端 H5；共享 Tailwind/daisyUI 技术方式与动效，不共享后台配色和布局假设。
- `python-service-ops`：读取本项目的 `ops/project.toml`，统一启停与状态。
- 后续 `fastapi-service`：前后端分离项目使用；Nuxt 项目不引入 FastAPI。

## 不要做的事

- 不要在 `app/` 或 `shared/` 里 import 数据库、Drizzle、pg、node 内置模块；
- 不要在页面里直接写 `$fetch` 之外的数据库查询；
- 不要把 token 放 localStorage；
- 不要手改已应用的迁移；
- 不要用 `npm` / `yarn` / `bun`；
- 不要用浮点数算金额；
- 不要在 Nuxt 项目里再套一层 FastAPI 或网关；
- 不要为了“统一”把 H5 的底部导航、`max-w-md` 布局硬套到管理后台。
