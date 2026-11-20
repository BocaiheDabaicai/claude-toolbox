# 认证

## 1. 流程

```
POST /api/auth/login
  → 校验 email + password
  → Argon2 验证 password_hash
  → 签发 JWT（sub=user.id, email, role, exp）
  → 返回 { token, user }

后续请求
  → Access-Token: <token>
  → get_current_user 解码 JWT
  → 查询 users 表确认账号仍存在且 active
  → 注入 User
```

## 2. 密码

`app/core/security.py`：

- `pwdlib.PasswordHash.recommended()`（Argon2）；
- `hash_password` / `verify_password`；
- 不在日志、错误、响应中输出密码或 hash。

## 3. JWT

- 算法：HS256（`JWT_ALGORITHM`）；
- 密钥：`JWT_SECRET`，至少 32 位；
- 过期：`ACCESS_TOKEN_EXPIRE_MINUTES`，默认 720 分钟；
- payload：`sub`、`email`、`role`、`iat`、`exp`；
- 解码失败统一返回 401。

生产：

- 必须替换默认开发密钥；
- `ENVIRONMENT=production` 时使用默认密钥会直接启动失败；
- 后续可加 refresh token、密钥轮换、黑名单。

## 4. 请求头

优先：

```
Access-Token: <token>
```

兼容：

```
Authorization: Bearer <token>
```

与现有 H5 `src/utils/request.js` 一致：请求拦截器注入 `Access-Token`。

## 5. 依赖

```python
async def get_current_user(
    token: Annotated[str, Depends(extract_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    payload = decode_access_token(token)
    user = await session.get(User, int(payload["sub"]))
    if not user or user.status != "active":
        raise ApiError(401, "账号不存在或已停用")
    return user
```

路由：

```python
user: CurrentUser
```

## 6. 登录失败

- 账号不存在、密码错误、账号停用统一返回 `401 "邮箱或密码不正确"`；
- 不泄露账号是否存在；
- 后续增加登录失败限流/锁定。

## 7. 退出

JWT 无状态：`POST /api/auth/logout` 返回成功，客户端删除 token。

## 8. 安全清单

- [ ] `JWT_SECRET` 至少 32 位，服务器 `.env` 权限 600；
- [ ] 生产 `ENVIRONMENT=production`；
- [ ] 生产 `DOCS_ENABLED=false`；
- [ ] CORS 只允许实际前端域名；
- [ ] 登录错误不区分账号/密码；
- [ ] 密码使用 Argon2；
- [ ] 不在 URL 查询参数传 token；
- [ ] 后续增加登录限流、refresh token、密钥轮换；
- [ ] 管理员 seed 密码首次登录后修改。
