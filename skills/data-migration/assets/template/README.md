# __PROJECT_TITLE__ 数据迁移

由 `data-migration` Skill 生成的工作区。

## 1. 安装迁移工具

```bash
uv tool install <skill-path>/assets/kit
# 需要 MySQL / Excel 源：
uv tool install '<skill-path>/assets/kit[all]'
```

## 2. 配置

- `migration.toml`：源、目标、映射、批次、断点、对账；
- `mapping.csv`：字段映射与转换；
- `transforms.py`：项目自定义转换；
- `data/`：CSV / Excel 源文件；
- `docs/`：迁移计划、对账记录、切换清单。

目标 DSN 从环境变量读取：

```bash
export TARGET_DSN='postgresql://user:pass@host:5432/app_db'
export SOURCE_DSN='postgresql://user:pass@host:5432/legacy_db'
```

## 3. 执行顺序

```bash
migration-kit profile --config migration.toml --out docs/profile.md
migration-kit plan --config migration.toml
migration-kit run --config migration.toml            # dry-run，不写库
migration-kit run --config migration.toml --limit 100 # 小批量 dry-run
migration-kit run --config migration.toml --apply    # 真正写入
migration-kit reconcile --config migration.toml --out docs/reconcile.md
```

## 4. 安全

- 源库只读；目标写入前先 `pg_dump` 备份；
- `run` 默认 dry-run，确认样例和计数后再 `--apply`；
- `run.key` 必须对应目标表唯一索引，保证幂等 upsert；
- 断点保存在 `.migration-state.json`，失败后修复数据再续跑；
- 切换前冻结源写入、跑最终增量、对账通过再切应用。
