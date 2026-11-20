# migration-kit

PostgreSQL 数据迁移工具：源数据画像、映射校验、dry-run、批量 upsert、断点续跑、对账。

## 安装

```bash
# 基础：CSV / PostgreSQL 源，PostgreSQL 目标
uv tool install .

# 需要 MySQL / Excel 源
uv tool install '.[all]'
```

## 命令

```bash
migration-kit profile --config migration.toml --out profile.md
migration-kit plan --config migration.toml
migration-kit run --config migration.toml            # dry-run
migration-kit run --config migration.toml --apply    # 真正写入
migration-kit reconcile --config migration.toml --out reconcile.md
```

- `run` 默认 dry-run，只有 `--apply` 才写目标库；
- `run --limit N` 只处理前 N 行；
- `run --reset-state` 忽略断点；
- 断点保存在 `run.state_file`。

## 配置

`migration.toml`：

```toml
[source]
type = "csv"                    # csv | excel | postgres | mysql
path = "data/customers.csv"
# dsn = "${SOURCE_DSN}"         # postgres/mysql
# schema = "public"
# table = "legacy_customers"
# cursor_column = "id"          # 可选：数据库源断点续跑
# where = "deleted_at is null"

[target]
dsn = "${TARGET_DSN}"
schema = "public"
table = "customers"

[mapping]
file = "mapping.csv"
transform_module = "transforms"

[run]
batch_size = 1000
key = ["legacy_id"]             # 目标表唯一键，用于 ON CONFLICT
state_file = ".migration-state.json"
sample_limit = 5
on_error = "stop"               # stop | skip
```

`mapping.csv`：

```csv
target_column,source_column,target_type,required,default,transform
legacy_id,id,bigint,true,,trim
name,name,text,true,,trim
phone,phone,text,false,,digits
email,email,text,false,,lower
status,status,text,true,active,lower
```

- `target_type`：text / varchar / int / bigint / numeric / boolean / date / timestamptz / uuid；
- 内置 transform：trim / lower / upper / digits / decimal / bool / date / datetime / uuid / identity；
- 自定义 transform 写在 `transforms.py`：

```python
STATUS_MAP = {"1": "active", "0": "inactive"}

def map_status(value, row):
    if value is None:
        return "active"
    return STATUS_MAP.get(str(value).strip(), str(value).strip().lower())

TRANSFORMS = {"map_status": map_status}
```

## 安全

- 源库只读；目标写入前先备份；
- `run` 默认 dry-run，确认后再 `--apply`；
- `key` 必须对应目标表唯一索引，保证 `ON CONFLICT` 幂等；
- 目标表由项目自身迁移创建，本工具不建表、不删表；
- `where` / 对账 SQL 来自本地可信配置，不拼接外部输入；
- 生产 cutover 前先冻结源写入、跑最终增量、对账通过再切换。
