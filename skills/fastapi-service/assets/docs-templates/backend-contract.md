# 后端契约

> 项目：__PROJECT_TITLE__
> 更新日期：YYYY-MM-DD

## 1. 环境

| 环境 | Base URL | 数据库 | 备注 |
|---|---|---|---|
| 开发 | http://127.0.0.1:8000 | app___PROJECT_DB__ | 本地 |
| 测试 |  |  |  |
| 生产 |  |  | HTTPS |

## 2. 认证

- 登录：`POST /api/auth/login`
- 请求体：`{ "email": "...", "password": "..." }`
- 成功：`data.token` + `data.user`
- 后续请求头：`Access-Token: <token>`（兼容 `Authorization: Bearer <token>`）
- 401：清 token，回登录页

## 3. 响应结构

成功：

```json
{ "code": 200, "message": "ok", "data": {} }
```

列表：

```json
{ "code": 200, "message": "ok", "data": { "rows": [], "total": 0, "page": 1, "pageSize": 20 } }
```

错误：

```json
{ "code": 400, "message": "请求参数不合法", "data": null, "details": [] }
```

## 4. 接口清单

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/healthz` | 存活 | 否 |
| GET | `/api/readyz` | 就绪（含数据库） | 否 |
| POST | `/api/auth/login` | 登录 | 否 |
| GET | `/api/auth/me` | 当前用户 | 是 |
| POST | `/api/auth/logout` | 退出（客户端删 token） | 是 |
| GET | `/api/customers?page=1&pageSize=20&search=` | 客户列表 | 是 |
| GET | `/api/customers/{id}` | 客户详情 | 是 |
| POST | `/api/customers` | 新建客户 | 是 |
| PUT | `/api/customers/{id}` | 更新客户 | 是 |
| DELETE | `/api/customers/{id}` | 软删客户 | 是 |

## 5. 错误码

| code | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 参数/请求体不合法 |
| 401 | 未登录/凭证过期/账号密码错误 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 冲突 |
| 500 | 服务器内部错误 |

## 6. 字段约定

- JSON 字段：前端使用 camelCase（`createdAt` / `pageSize`）；
- 数据库字段：snake_case；
- 时间：ISO 8601，带时区；
- 金额：后续使用 decimal，不返回浮点误差值。

## 7. 已知坑

| 日期 | 问题 | 处理 |
|---|---|---|
|  |  |  |
