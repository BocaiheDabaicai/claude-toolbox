# 后端测试

## 1. 工具

- pytest；
- pytest-asyncio（async）；
- httpx `ASGITransport` / `AsyncClient`；
- 独立测试 PostgreSQL；
- 迁移在测试启动前执行。

## 2. 分层

| 层 | 测什么 |
|---|---|
| 单元 | 纯函数、密码、JWT、校验、金额 |
| API | 登录、CRUD、错误码、权限、分页 |
| 集成 | 数据库约束、事务、迁移 |
| 契约 | OpenAPI/响应结构 |
| E2E | 与前端联调的关键链路 |

## 3. 测试客户端

```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

## 4. 测试数据库

- 独立 `app_test`；
- 测试前 `alembic upgrade head`；
- 每个用例事务回滚，或每个文件重建 schema；
- 不连开发/生产库；
- 测试结束清理数据。

依赖覆盖示例：

```python
async def override_session():
    async with TestSession() as session:
        yield session

app.dependency_overrides[get_session] = override_session
```

## 5. 认证

- 测试用户/测试 token；
- 未登录 401、过期 401、越权 403；
- 不在测试里写真实密码；
- 密码 hash 测试用固定输入。

## 6. 迁移

- CI 每次跑 `alembic upgrade head`；
- 迁移失败即门禁失败；
- 不手改已应用迁移；
- 迁移测试库用独立 database。

## 7. 断言

- 状态码 + `{ code, message, data }`；
- 关键字段值；
- 数据库副作用；
- 幂等/重复提交；
- 分页 total/pageSize；
- 错误 `details`。

## 8. 门禁

```bash
uv run pytest
uv run ruff check .
uv run alembic upgrade head
```

- 测试失败不发布；
- lint 失败不发布；
- 迁移失败不发布。
