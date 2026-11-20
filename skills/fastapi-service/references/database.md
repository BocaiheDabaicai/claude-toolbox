# 数据库与异步 SQLAlchemy

## 1. 连接

`app/db/session.py`：

```python
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

- URL 使用 `postgresql+asyncpg://`；
- 每个项目独立 database；
- `pool_pre_ping` 防止连接被数据库主动断开；
- `expire_on_commit=False`，提交后仍可读取对象字段。

## 2. 模型

`app/db/models.py` 使用 SQLAlchemy 2 类型化模型：

```python
class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    ...
```

约定：

- 主键 `BigInteger` + `Identity`；
- 审计字段 `created_at` / `updated_at`；
- 软删 `deleted_at`；
- 枚举先用 `String`，校验在 Pydantic；
- 金额用 `Numeric`，不用 Float。

## 3. 会话依赖

```python
async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

路由：

```python
session: Annotated[AsyncSession, Depends(get_session)]
```

不要在模块顶层创建会话；不要跨请求复用会话。

## 4. 查询

### 列表 + 搜索 + 分页

```python
conditions = [Customer.deleted_at.is_(None)]
if search:
    like = f"%{search}%"
    conditions.append(or_(
        Customer.name.ilike(like),
        Customer.phone.ilike(like),
        Customer.company.ilike(like),
    ))

total = await session.scalar(select(func.count(Customer.id)).where(*conditions)) or 0
rows = await session.execute(
    select(Customer)
    .where(*conditions)
    .order_by(Customer.created_at.desc())
    .offset((page - 1) * page_size)
    .limit(page_size)
)
```

- 先 count 再查 rows；
- 固定排序；
- `page_size` 上限 100；
- 用户输入不拼 SQL 字符串。

### 软删

```python
customer.deleted_at = datetime.now(UTC)
await session.commit()
```

所有查询带 `Customer.deleted_at.is_(None)`。

### 事务

多表写入：

```python
async with session.begin():
    # ...
```

或者显式 `commit()`；失败时 `rollback()`。

## 5. Alembic

```bash
uv run alembic revision --autogenerate -m "add customer"
uv run alembic upgrade head
uv run alembic history
uv run alembic downgrade -1
```

规则：

- 已应用迁移不改；
- 迁移文件提交；
- 生产迁移由 `opsctl` 的 oneshot 执行；
- `migrations/env.py` 从 `get_settings()` 读取 URL，支持 asyncpg；
- 离线生成 SQL：`uv run alembic upgrade head --sql`。

## 6. 索引

- 搜索字段：`name`、`phone`；
- 排序字段：`created_at`；
- 软删过滤：`deleted_at`；
- 唯一字段：`users.email`；
- 用 `EXPLAIN ANALYZE` 验证慢查询。

## 7. 常见坑

- **同步调用**：误用 `create_engine`/`Session` 会阻塞事件循环；统一 async。
- **asyncpg 参数**：批量插入用 `insert().values([...])`，不要拼接 SQL。
- **count 类型**：`session.scalar` 可能返回 `None`，用 `or 0`。
- **日期时区**：统一 `DateTime(timezone=True)`，Python 用 `datetime.now(UTC)`。
- **N+1**：列表需要关联数据时用 `selectinload`，不要在循环里查。
- **连接泄漏**：使用 `async with SessionLocal()` 依赖，不手动长期持有。
- **迁移缺模型导入**：`migrations/env.py` 必须 import `app.db.models`，否则 autogenerate 看不到表。
