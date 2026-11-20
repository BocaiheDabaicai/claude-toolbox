# data-migration

PostgreSQL 数据迁移 Skill：源数据画像、字段映射、dry-run、批量 upsert、断点续跑、对账、切换与回滚。

## 前置要求

- Python 3.11+
- uv
- 目标 PostgreSQL
- 源：CSV / Excel / PostgreSQL / MySQL

## 快速开始

```bash
# 1. 生成迁移工作区
python .claude/skills/data-migration/scripts/scaffold.py ../crm-migration \
  --name crm-migration \
  --title "CRM 数据迁移"

# 2. 安装迁移工具
uv tool install .claude/skills/data-migration/assets/kit
# 需要 MySQL / Excel 源：uv tool install '.claude/skills/data-migration/assets/kit[all]'

# 3. 配置
cd ../crm-migration
export TARGET_DSN='postgresql://user:pass@host:5432/app_db'
# PostgreSQL / MySQL 源再 export SOURCE_DSN

# 4. 画像、映射检查、dry-run
migration-kit profile --config migration.toml --out docs/profile.md
migration-kit plan --config migration.toml
migration-kit run --config migration.toml

# 5. 备份后正式加载
pg_dump ... > backup.sql
migration-kit run --config migration.toml --apply

# 6. 对账
migration-kit reconcile --config migration.toml --out docs/reconcile.md
```

## 目录

```
data-migration/
├─ SKILL.md
├─ README.md
├─ references/              # playbook、画像、映射、加载、对账、切换、排错
├─ assets/
│  ├─ kit/                  # Python 工具 + tests
│  ├─ template/             # 迁移工作区模板
│  └─ docs-templates/       # 迁移计划 / 对账 / 切换清单
└─ scripts/
   └─ scaffold.py           # 生成工作区
```

## 工具能力

| 命令 | 作用 |
|---|---|
| `profile` | 行数、空值、空字符串、去重、样例 |
| `plan` | 校验映射、类型、transform、key |
| `run` | 默认 dry-run；`--apply` 批量 upsert；断点续跑 |
| `reconcile` | 执行配置中的 SQL 对账 |

## 安全

- 源库只读；
- 目标先备份；
- 默认 dry-run；
- `run.key` + 唯一索引保证幂等；
- 对账通过再 cutover。

## 版本记录

| 版本 | 日期 | 内容 |
| --- | --- | --- |
| 0.1.0 | 2026-11-20 | 初始版本：migration-kit（CSV/Excel/PostgreSQL/MySQL 源、PostgreSQL 目标）、画像、映射、dry-run、upsert、断点、对账、切换模板；22 个测试通过 |
