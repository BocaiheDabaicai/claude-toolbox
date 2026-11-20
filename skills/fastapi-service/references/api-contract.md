# 接口契约

## 1. 响应结构

成功：

```json
{ "code": 200, "message": "ok", "data": {} }
```

列表：

```json
{
  "code": 200,
  "message": "ok",
  "data": { "rows": [], "total": 0, "page": 1, "pageSize": 20 }
}
```

错误：

```json
{
  "code": 400,
  "message": "请求参数不合法",
  "data": null,
  "details": [{ "path": "body.email", "message": "Field required" }]
}
```

- `code` 与 HTTP 状态码一致；
- 错误不返回业务数据；
- `details` 可选，用于字段级错误。

## 2. 分页

请求：

```
GET /api/customers?page=1&pageSize=20&search=张
```

- `page` 从 1 开始；
- `pageSize` 1–100，默认 20；
- `search` 最长 100。

响应：

```json
{
  "code": 200,
  "message": "ok",
  "data": { "rows": [], "total": 0, "page": 1, "pageSize": 20 }
}
```

## 3. 错误码

| code | 含义 | 前端处理 |
|---|---|---|
| 200 | 成功 | 取 `data` |
| 400 | 参数/请求体不合法 | 展示 `message` / 字段错误 |
| 401 | 未登录/过期/凭证错误 | 清 token，回登录 |
| 403 | 无权限 | 提示 |
| 404 | 资源不存在 | 空态或提示 |
| 409 | 冲突 | 提示 |
| 500 | 服务器内部错误 | 通用提示 + 重试 |

## 4. 接口清单

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/healthz` | 存活 | 否 |
| GET | `/api/readyz` | 就绪（数据库） | 否 |
| POST | `/api/auth/login` | 登录 | 否 |
| GET | `/api/auth/me` | 当前用户 | 是 |
| POST | `/api/auth/logout` | 退出 | 是 |
| GET | `/api/customers` | 列表/搜索/分页 | 是 |
| GET | `/api/customers/{id}` | 详情 | 是 |
| POST | `/api/customers` | 新建 | 是 |
| PUT | `/api/customers/{id}` | 更新 | 是 |
| DELETE | `/api/customers/{id}` | 软删 | 是 |

## 5. 字段

- 前端 JSON：camelCase（`createdAt`、`updatedAt`、`deletedAt`、`pageSize`）；
- 数据库：snake_case；
- 时间：ISO 8601 带时区；
- 软删客户不会出现在列表/详情/更新/删除结果中。

## 6. 与 H5 请求层对接

现有 `frontend-h5-project` 的 `src/utils/request.js`：

- 请求头注入 `Access-Token`；
- `res.code === 200` 视为成功；
- `1001` / 401 清 token 回登录；
- 其他 code 默认 toast。

因此后端：

- 成功业务响应 HTTP 200 + `code: 200`；
- 401 使用 HTTP 401 + `code: 401`；
- 错误 `message` 必须是可直接展示的中文/英文文案；
- 列表放在 `data.rows` / `data.total` / `data.page` / `data.pageSize`。

## 7. 幂等（后续）

- 写接口可接受 `Idempotency-Key`；
- 服务端缓存请求指纹 + 响应；
- 重放返回同一结果；
- 当前模板未实现，按业务需要补充。
