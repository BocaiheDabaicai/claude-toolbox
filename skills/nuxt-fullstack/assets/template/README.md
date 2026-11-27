# __PROJECT_TITLE__

Nuxt 4 全栈业务应用模板：页面、API、PostgreSQL 直连、Cookie 会话、Pinia 状态、Drizzle 迁移和 `opsctl` 运维清单。

## 前置要求

- Node.js 22.19+ / 24.11+ / 26+
- pnpm 9.15.9
- PostgreSQL

## 快速开始

```bash
cp .env.example .env
# 修改 NUXT_DATABASE_URL、NUXT_SESSION_SECRET、SEED_ADMIN_*

pnpm install
pnpm db:generate
pnpm db:migrate
pnpm db:seed
pnpm dev
```

打开 `http://localhost:3000`，使用 `.env` 中的管理员账号登录。

## 常用命令

```bash
pnpm dev                 # 开发
pnpm build               # 生产构建
pnpm start               # 运行 .output
pnpm check               # 边界检查 + 类型检查
pnpm db:generate         # schema -> SQL 迁移
pnpm db:migrate          # 应用迁移
pnpm db:seed             # 管理员 + 示例客户
```

## 界面

后台主题为「石墨侧栏 × 冷白内容 × 深湖蓝」：

- 颜色令牌：`app/assets/css/colors.css`
- 面板、表格、状态标签等结构样式：`app/assets/css/admin.css`
- 侧栏与面包屑导航配置：`app/utils/navigation.ts`

颜色只用语义类，新增色值先登记 `colors.css`；禁止在组件里写裸色值、渐变或大圆角重投影。

## 目录

```
app/                      # 页面、布局、组件、composable、Pinia store、样式
├─ assets/css/            # 设计令牌与全局样式
├─ components/            # AppSidebar / AppTopbar / AppNavIcon / PageHeader / EmptyState
├─ composables/useAuth.ts # useAuth() 兼容层
├─ stores/auth.ts         # Pinia 登录态
├─ layouts/               # default（后台）/ auth（登录）
├─ middleware/            # 全局登录守卫
├─ pages/                 # 登录、仪表盘、客户、设置
└─ utils/                 # 导航配置、日期格式化等
server/                   # 仅服务端
├─ api/                   # healthz / readyz / auth / customers
├─ database/              # Drizzle schema 与迁移
├─ middleware/            # API 会话校验
└─ utils/                 # db / session / password / response / validation
shared/                   # 客户端与服务端共享
├─ schemas/               # Zod 输入校验
└─ types/                 # API 与会话类型
ops/project.toml          # opsctl 清单
scripts/                  # 环境检查、边界检查、seed
```

## 接口约定

所有业务接口返回：

```json
{ "code": 200, "message": "ok", "data": {} }
```

错误：

```json
{ "code": 400, "message": "请求参数不合法", "data": null, "details": [] }
```

分页：

```json
{ "code": 200, "message": "ok", "data": { "rows": [], "total": 0, "page": 1, "pageSize": 10 } }
```

## 运维

```bash
# 在服务器上由 python-service-ops 的 opsctl 管理
opsctl status __PROJECT_NAME__ --root /srv/projects
opsctl install __PROJECT_NAME__ --root /srv/projects
opsctl install __PROJECT_NAME__ --root /srv/projects --apply
```

`ops/project.toml` 已声明迁移（oneshot，先于 web）和健康检查 `/api/healthz`。

## 安全

- `.env` 不入库，服务器上 `chmod 600`。
- `NUXT_SESSION_SECRET` 至少 32 位随机字符。
- 生产环境建议 HTTPS；若暂时只有 HTTP，把 `NUXT_PUBLIC_SECURE_COOKIES` 设为 `false`。
- 不在 `app/` 或 `shared/` 中引用数据库、`pg`、`drizzle-orm`、`node:*`；`pnpm check:boundary` 会拦截。
