# 架构

## 1. 模块化单体

一个 FastAPI 进程，按业务域分模块；共享一个数据库和事务边界。

```
app/
├─ main.py
├─ api.py
├─ core/
│  ├─ config.py
│  ├─ security.py
│  ├─ errors.py
│  ├─ responses.py
│  ├─ handlers.py
│  └─ middleware.py
├─ db/
│  ├─ base.py
│  ├─ models.py
│  └─ session.py
└─ modules/
   ├─ auth/
   ├─ customers/
   └─ health/
```

先做模块化单体；只有当某个模块确实需要独立扩容、独立发布或独立数据边界时，才拆服务。

## 2. 分层

```
HTTP → router → service → repository → SQLAlchemy → PostgreSQL
              ↓
           schema (Pydantic)
```

| 层 | 职责 | 禁止 |
|---|---|---|
| router | 参数、依赖、响应、HTTP 状态 | 写 SQL、堆业务规则 |
| service | 业务规则、权限、错误 | 依赖 FastAPI Request |
| repository | SQLAlchemy 查询、持久化 | 处理 HTTP |
| schema | 输入/输出校验 | 访问数据库 |
| core | 配置、安全、错误、响应、中间件 | 业务逻辑 |

## 3. 请求流

1. `request_context_middleware` 生成/透传 `X-Request-ID`，记录耗时；
2. CORS 中间件处理跨域；
3. 依赖注入：`get_session` 提供 `AsyncSession`，`get_current_user` 校验 `Access-Token`；
4. router 调用 service；
5. service 调用 repository；
6. 返回 `{ code, message, data }`；
7. 异常由全局 handler 转成统一错误结构。

## 4. 响应封装

`app/core/responses.py`：

```python
class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "ok"
    data: T | None = None

class Page(BaseModel, Generic[T]):
    rows: list[T]
    total: int
    page: int
    pageSize: int
```

- 成功统一 `ok(data)`；
- 列表 `Page` 的 `pageSize` 使用 camelCase，与前端一致；
- FastAPI 的 `response_model=ApiResponse[...]` 负责 OpenAPI 文档与序列化；
- 错误不返回 `data` 对象，只返回 `data: null` 和可选 `details`。

## 5. 错误处理

`ApiError(code, message, details=None)`：

- `code` 同时作为 HTTP 状态码；
- 业务错误在 service/router 抛；
- `handlers.py` 注册：
  - `ApiError` → 对应状态码 + `{ code, message, data: null, details? }`；
  - `RequestValidationError` → 400 + 字段错误列表；
  - 未捕获 `Exception` → 500，记录堆栈，不返回内部细节。

## 6. 配置

`app/core/config.py` 使用 `pydantic-settings`：

| 配置 | 环境变量 | 默认 |
|---|---|---|
| `app_name` | `APP_NAME` | FastAPI Service |
| `environment` | `ENVIRONMENT` | development |
| `database_url` | `DATABASE_URL` | 本地 app_dev |
| `jwt_secret` | `JWT_SECRET` | 开发默认，生产必须替换 |
| `jwt_algorithm` | `JWT_ALGORITHM` | HS256 |
| `access_token_expire_minutes` | `ACCESS_TOKEN_EXPIRE_MINUTES` | 720 |
| `cors_origins` | `CORS_ORIGINS` | http://localhost:5173 |
| `docs_enabled` | `DOCS_ENABLED` | true |

`get_settings()` 使用 `lru_cache`，进程内只读一次。

## 7. CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- 使用 `Access-Token` 头，不依赖 Cookie，所以 `allow_credentials=False`；
- 生产只配置实际前端域名；
- 如果未来改用 Cookie 会话，需要 `allow_credentials=True` 且不能用 `*`。

## 8. Lifespan

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()
```

- 启动不强制连库，避免数据库短暂不可用时整个服务起不来；
- 关闭时释放连接池；
- 数据库就绪由 `/api/readyz` 报告。

## 9. OpenAPI

- 开发环境：`/docs`、`/openapi.json`；
- 生产环境：`DOCS_ENABLED=false` 关闭；
- 新增 router 时设置 `tags`，保持文档分组清晰；
- 前端可以从 OpenAPI 生成 TypeScript 类型（后续扩展）。
