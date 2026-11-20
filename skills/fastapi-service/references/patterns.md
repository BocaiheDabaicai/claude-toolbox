# 业务模式

## 1. 新增一个业务模块

1. `app/db/models.py` 加表/字段；
2. `uv run alembic revision --autogenerate -m "add xxx"`；
3. 检查生成的迁移，补索引/默认值；
4. `app/modules/<domain>/schemas.py`：输入/输出；
5. `repository.py`：查询与持久化；
6. `service.py`：业务规则、错误；
7. `router.py`：HTTP 参数、依赖、响应；
8. `app/api.py` 挂载；
9. 补 `tests/test_<domain>.py`；
10. 更新 `docs/backend-contract.md` / `docs/data-model.md`。

## 2. 列表 / 搜索 / 分页

Query 参数：

```python
page: Annotated[int, Query(ge=1)] = 1
page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20
search: Annotated[str, Query(max_length=100)] = ""
```

Repository：

```python
conditions = [Model.deleted_at.is_(None)]
if search:
    like = f"%{search}%"
    conditions.append(or_(Model.name.ilike(like), Model.phone.ilike(like)))

total = await session.scalar(select(func.count(Model.id)).where(*conditions)) or 0
rows = await session.execute(
    select(Model)
    .where(*conditions)
    .order_by(Model.created_at.desc())
    .offset((page - 1) * page_size)
    .limit(page_size)
)
```

返回 `Page`，字段 `rows/total/page/pageSize`。

## 3. 创建 / 更新

- 输入用 Pydantic schema；
- 空字符串转 `None`；
- 创建后 `refresh` 再返回；
- 更新用完整表单（PUT），字段全部覆盖；
- 不存在抛 `ApiError(404, "客户不存在")`。

## 4. 软删除

```python
model.deleted_at = datetime.now(UTC)
await session.commit()
```

- 列表/详情/更新/删除都过滤 `deleted_at IS NULL`；
- 不提供物理删除，除非业务明确要求；
- 软删数据保留策略需要业务确认。

## 5. 校验

- Pydantic `Field` 限制长度/范围；
- `EmailStr` 校验邮箱；
- 枚举用 `Literal`；
- 错误由全局 handler 转 400；
- 不在 router 里手写 `if not ...` 字段校验。

## 6. 事务

多表写入：

```python
async with session.begin():
    session.add(order)
    session.add(order_item)
```

或显式 `commit` / `rollback`；不要让异常吞掉事务。

## 7. 幂等

写接口如涉及重试/第三方回调：

- 接受 `Idempotency-Key`；
- 用唯一键或幂等表记录请求指纹；
- 重复请求返回第一次结果；
- 当前模板未实现，按业务补充。

## 8. Seed

- 管理员从环境变量读取；
- 示例数据只在表为空时插入；
- 可重复执行；
- 不写真实客户数据；
- 生产 seed 只在首次部署执行。

## 9. 日志

- request_id 中间件记录方法/路径/状态/耗时；
- 业务错误记录 code/message，不记录密码/token；
- 未捕获异常 `logger.exception`；
- 生产日志走 stdout/stderr，由 systemd/journal 收集。

## 10. 反模式

- router 里直接 `session.execute(select(...))`；
- sync `Session` 混进 async 路由；
- 返回裸数组或 `{"data": ...}`；
- 每个模块自己写 try/except 返回不同结构；
- 在服务层依赖 `Request`/`HTTPException`；
- 手改已应用的迁移；
- 用 `float` 存金额；
- 在代码里写死数据库地址、JWT secret、管理员密码。
