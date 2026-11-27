# 认证与会话

## 1. 流程

```
POST /api/auth/login
  → 校验邮箱/密码
  → 生成 HMAC 签名会话
  → Set-Cookie: app_session=...; HttpOnly; SameSite=Lax
  → 返回当前用户

GET /api/**（受保护）
  → server/middleware/auth.ts 读取并校验 Cookie
  → 写入 event.context.user
  → 路由 handler 使用 requireUser(event)
```

## 2. 密码

`server/utils/password.ts` 使用 Node 内置 `scrypt`：

- 随机 16 字节 salt；
- N=16384、r=8、p=1、keylen=64；
- 存储格式：`scrypt$N$r$p$saltBase64$hashBase64`；
- 校验使用 `timingSafeEqual`。

密码策略：

- 登录：非空、最长 128；
- 创建/seed：至少 8 位；
- 不在日志、错误信息、响应里输出密码或 hash。

## 3. 会话

`server/utils/session.ts`：

- 负载：`{ id, email, name, role, iat, exp }`；
- 签名：`HMAC-SHA256(secret, base64url(payload))`；
- Cookie：`HttpOnly`、`SameSite=Lax`、生产 `Secure`、`Path=/`、7 天；
- 密钥至少 32 位，来自 `NUXT_SESSION_SECRET`；
- 会话是签名不是加密，不要把敏感信息放 payload。

## 4. 服务端校验

`server/middleware/auth.ts`：

- 只保护 `/api/**`；
- 公开路径：`/api/auth/login`、`/api/auth/logout`、`/api/healthz`、`/api/readyz`；
- 无会话返回 `401 { code, message, data: null }`；
- 有会话写入 `event.context.user`。

路由内用 `requireUser(event)` 获取当前用户。

## 5. 页面守卫

`app/middleware/auth.global.ts`：

- 未登录访问业务页 → `/login?redirect=...`；
- 已登录访问 `/login` → `/`；
- SSR 时 `useRequestFetch()` 自动转发 Cookie；
- 页面里的受保护请求统一用 `useApiFetch()`（内部在服务端使用 `useRequestFetch`），不要直接用裸 `useFetch`；
- 用户状态放 Pinia store（`app/stores/auth.ts`），`initialized` 标记避免每次导航重复请求；页面通过 `useAuth()` 兼容层访问。

## 6. CSRF

Cookie 会话需要防 CSRF：

- 所有写接口调用 `requireSameOrigin(event)`；
- 比较 `Origin` 与 `Host`/`X-Forwarded-Host`；
- 浏览器同源 POST 会带 `Origin`；非浏览器客户端没有 Origin 时放行（依赖会话和网络边界）；
- 反向代理必须保留 Host 或设置 `X-Forwarded-Host`。

## 7. 安全清单

- [ ] `NUXT_SESSION_SECRET` 至少 32 位，服务器 `.env` 权限 600；
- [ ] 生产 HTTPS；只有 HTTP 时 `NUXT_PUBLIC_SECURE_COOKIES=false`；
- [ ] 不把 token 放 localStorage；
- [ ] 不在客户端代码里读 `NUXT_SESSION_SECRET`；
- [ ] 错误提示不区分“账号不存在”和“密码错误”；
- [ ] 写接口都有同源检查；
- [ ] 登录接口后续增加限流/失败次数限制；
- [ ] 密钥轮换时接受旧 Cookie 短暂失效。

## 8. 后续扩展

- 角色权限：`role` 已写入会话，可在 `server/utils/session.ts` 增加 `requireRole(event, 'admin')`；
- 账号禁用：当前会话最多 7 天有效；如需即时失效，在中间件里按 `id` 查库；
- 刷新/滑动过期：可在访问时重签 Cookie；
- 多因素认证：登录成功后增加第二步。
