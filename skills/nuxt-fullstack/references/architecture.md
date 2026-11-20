# 架构

## 1. 目录边界

```
app/          客户端 + SSR：页面、布局、组件、composable、样式
server/       仅服务端：API、数据库、会话、密码、校验
shared/       共享：Zod schema、API 类型、业务类型
public/       静态资源
ops/          project.toml
docs/         项目文档
```

Nuxt 4 默认 `srcDir = app/`，服务端目录固定在根目录 `server/`。

## 2. 请求链路

```
浏览器
  │  页面 / SSR
  ▼
Nuxt (app/)
  │  $fetch / useFetch
  ▼
server/api/**
  │  Zod 校验 + 会话
  ▼
server/utils/db.ts
  │  Drizzle
  ▼
PostgreSQL
```

- 页面不直连数据库，只调用 `/api/**`。
- `server/utils` 自动导入到服务端代码；业务路由仍建议显式 import 关键模块。
- `shared/` 只放同构代码（Zod、类型、纯函数），不能碰数据库。

## 3. 响应结构

成功：

```json
{ "code": 200, "message": "ok", "data": {} }
```

错误：

```json
{
  "code": 400,
  "message": "请求参数不合法",
  "data": null,
  "details": [{ "path": "name", "message": "姓名不能为空" }]
}
```

分页：

```json
{
  "code": 200,
  "message": "ok",
  "data": { "rows": [], "total": 0, "page": 1, "pageSize": 10 }
}
```

- HTTP 状态码与 `code` 保持一致；
- 业务错误抛 `ApiError(statusCode, code, message, details)`；
- `defineApiHandler` 统一捕获并输出错误结构；
- 未捕获异常返回 500，不向客户端暴露堆栈。

## 4. 认证与 SSR

- 登录成功后写入 HttpOnly Cookie；
- `server/middleware/auth.ts` 对 `/api/**` 做统一校验，公开路径只有登录、退出、healthz、readyz；
- `app/middleware/auth.global.ts` 在页面层做 SSR 重定向；
- `useAuth().fetchUser()` 在 SSR 时用 `useRequestFetch()` 转发 Cookie，客户端用 `$fetch`；
- 页面请求受保护接口统一用 `useApiFetch()`：服务端用 `useRequestFetch()` 转发 Cookie，客户端用 `$fetch`；同一 URL 有多个调用点时传唯一 `key`；
- 用户状态放在 `useState('auth.user')`，服务端渲染结果会序列化到客户端。

## 5. 服务端/客户端边界

允许：

```
app/  → shared/
server/ → shared/、server/
shared/ → shared/（仅纯代码）
```

禁止：

```
app/  → server/
shared/ → server/
app/ / shared/ → drizzle-orm / pg / node:*
```

`pnpm check:boundary` 会扫描 `app/` 与 `shared/`，发现越界立即失败。

## 6. Runtime Config

| 配置 | 环境变量 | 说明 |
|---|---|---|
| `databaseUrl` | `NUXT_DATABASE_URL` | PostgreSQL 连接串 |
| `sessionSecret` | `NUXT_SESSION_SECRET` | 至少 32 位随机字符 |
| `sessionCookieName` | `NUXT_SESSION_COOKIE_NAME` | 默认 `app_session` |
| `public.appName` | `NUXT_PUBLIC_APP_NAME` | 界面名称 |
| `public.secureCookies` | `NUXT_PUBLIC_SECURE_COOKIES` | 生产默认 true |

数据库地址缺失时服务仍能启动：`/api/healthz` 正常，`/api/readyz` 返回 503，便于运维定位。

## 7. 什么时候不该用 Nuxt 直连数据库

- 需要独立扩展后端、多个前端共用同一套 API；
- 后端需要复杂事务、任务队列、第三方回调、独立部署；
- 团队已有 FastAPI/Java 服务。

这类场景用 `frontend-h5-project` + 未来的 `fastapi-service`，而不是在 Nuxt 里再套一层网关。

## 8. 部署形态

- `pnpm build` 产出 `.output/`；
- `node .output/server/index.mjs` 启动 Node 服务；
- systemd 通过 `opsctl` 生成单元，`EnvironmentFile=.env`；
- `opsctl` 的 `migrate` oneshot 先执行迁移，失败时阻止 Web 启动。
