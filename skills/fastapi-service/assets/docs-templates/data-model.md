# 数据模型

> 项目：__PROJECT_TITLE__
> 数据库：PostgreSQL
> 更新日期：YYYY-MM-DD

## 1. 表清单

| 表 | 用途 | 软删 | 迁移版本 |
|---|---|---|---|
| users | 管理员/操作员 | 否 | 0001_init |
| customers | 客户资料 | 是（deleted_at） | 0001_init |

## 2. 字段

### users

| 字段 | 类型 | 可空 | 默认 | 说明 |
|---|---|---|---|---|
| id | bigint identity | 否 | 自增 | 主键 |
| email | varchar(255) | 否 |  | 唯一索引 |
| name | varchar(100) | 否 |  | 显示名 |
| password_hash | text | 否 |  | Argon2 |
| role | varchar(32) | 否 | admin | admin / operator |
| status | varchar(16) | 否 | active | active / disabled |
| created_at | timestamptz | 否 | now() |  |
| updated_at | timestamptz | 否 | now() |  |

### customers

| 字段 | 类型 | 可空 | 默认 | 说明 |
|---|---|---|---|---|
| id | bigint identity | 否 | 自增 | 主键 |
| name | varchar(100) | 否 |  | 姓名 |
| phone | varchar(32) | 是 |  | 电话 |
| email | varchar(255) | 是 |  | 邮箱 |
| company | varchar(200) | 是 |  | 公司 |
| note | text | 是 |  | 备注 |
| status | varchar(16) | 否 | active | active / inactive |
| created_at | timestamptz | 否 | now() |  |
| updated_at | timestamptz | 否 | now() |  |
| deleted_at | timestamptz | 是 |  | 软删时间 |

## 3. 索引

| 表 | 索引 | 字段 | 用途 |
|---|---|---|---|
| users | ix_users_email | email（unique） | 登录 |
| customers | ix_customers_name | name | 搜索 |
| customers | ix_customers_phone | phone | 搜索 |
| customers | ix_customers_created_at | created_at | 列表排序 |
| customers | ix_customers_deleted_at | deleted_at | 软删过滤 |

## 4. 迁移

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "add xxx"
```

已应用的迁移不修改，只追加新迁移。
