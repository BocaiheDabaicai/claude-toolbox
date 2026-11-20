# 接口契约测试

## 1. 契约

前后端以 **OpenAPI** 为契约：

- 后端生成 `/openapi.json`；
- 前端用 `openapi-typescript` 生成类型/客户端；
- 字段、枚举、分页、错误结构一致；
- 破坏性变更要显式评审。

## 2. 响应约定

```json
{ "code": 200, "message": "ok", "data": {} }
```

列表：

```json
{ "code": 200, "message": "ok", "data": { "rows": [], "total": 0, "page": 1, "pageSize": 20 } }
```

错误：

```json
{ "code": 400, "message": "...", "data": null, "details": [] }
```

## 3. 契约检查

- `/openapi.json` 200；
- 关键路径存在；
- schema 字段/类型符合预期；
- 前端生成的类型与后端一致；
- 分页/错误结构一致；
- 401 行为一致。

示例：

```python
async def test_openapi_has_customers(client):
    response = await client.get("/openapi.json")
    paths = response.json()["paths"]
    assert "/api/customers" in paths
```

## 4. Codegen

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts
```

- 生成文件提交仓库；
- CI 检查生成文件是否漂移；
- 不在手写类型里复制字段。

## 5. 破坏性变更

- 删字段、改类型、改枚举：破坏性；
- 新增可选字段：通常兼容；
- 分页/错误结构变化：破坏性；
- 变更前更新前端/文档/测试；
- 用 `/api/v1` 或兼容层过渡。

## 6. 联调检查

- 登录 → token → 带 `Access-Token`；
- 列表/分页/搜索；
- 创建/更新/删除；
- 401/403/404/400；
- 空态/错误态；
- CORS/同源。
