---
name: data-migration
description: 当用户要求“数据迁移”“旧库迁到 PostgreSQL”“MySQL/Excel/CSV 导入”“字段映射”“数据清洗”“迁移对账”“切换旧系统”，或需要一份可执行的数据迁移方案时使用。覆盖源数据画像、映射、dry-run、批量 upsert、断点续跑、对账、切换与回滚；不覆盖实时同步/CDC、持续双向同步、数据仓库建模。
version: 0.1.0
---

# 数据迁移

## 目标

把旧系统数据安全、可重复、可对账地迁移到 PostgreSQL。核心不是“把数据导进去”，而是：**画像清楚、映射可审、dry-run 可看、失败可续、结果可对账、切换可回滚**。

## 何时使用

- 旧系统 / 旧库迁到新 PostgreSQL；
- Excel、CSV、MySQL、PostgreSQL 数据导入；
- 需要字段映射、清洗、枚举转换、ID 映射；
- 需要迁移前画像、迁移后对账；
- 需要一次性切换旧系统，并准备回滚方案。

## 何时不用

- 实时同步、CDC、双向同步 → 用 Debezium / 业务双写等方案；
- 只是写个一次性 SQL 小脚本 → 直接写脚本，不必上完整流程；
- 数据仓库建模 / BI → 属于数仓项目；
- 目标不是 PostgreSQL → 需要替换目标适配器。

## 支持范围

| 角色 | 支持 |
|---|---|
| 目标 | PostgreSQL（psycopg 3） |
| 源 | CSV、Excel、PostgreSQL、MySQL |
| 扩展 | SQL Server / Oracle 需要新增 source adapter |
| 运行 | Python 3.11+，uv |

## 核心原则

1. **源库只读**：迁移工具不写源库。
2. **目标先备份**：`--apply` 前必须能恢复。
3. **dry-run 先行**：默认不写库，确认样例和错误后再 `--apply`。
4. **幂等 upsert**：`run.key` + 目标唯一索引，重复执行不产生重复数据。
5. **断点续跑**：失败后修复数据，从 state 继续。
6. **对账后切换**：数量、金额、抽样通过才 cutover。
7. **一切留痕**：画像、映射、dry-run、对账、切换清单都进 `docs/`。

## 标准工作流

### 0. 确认输入

- 源系统、源表/文件、目标库/表；
- 数据量、增量方式、停机窗口；
- 业务主键/唯一键；
- 字段所有者与验收人；
- 回滚方式。

### 1. 源数据画像

```bash
migration-kit profile --config migration.toml --out docs/profile.md
```

看：

- 总行数、空值、空字符串、去重值；
- 重复键、异常状态、日期范围、金额范围；
- 样例数据是否符合预期。

### 2. 字段映射

编辑 `mapping.csv` 与 `transforms.py`，然后：

```bash
migration-kit plan --config migration.toml
```

`plan` 必须无 ERROR；WARN 需要人工确认。

### 3. Dry-run

```bash
migration-kit run --config migration.toml
migration-kit run --config migration.toml --limit 100
```

检查：

- processed / would-write / skipped / errors；
- 样例字段值、枚举、日期、金额；
- 必填字段和默认值。

### 4. 正式加载

```bash
# 先备份目标库
pg_dump ... > backup.sql

migration-kit run --config migration.toml --apply
```

- 分批提交；
- 每批更新 state；
- 失败后修复数据，重新 `--apply` 续跑。

### 5. 对账

配置 `[[reconcile.checks]]`，然后：

```bash
migration-kit reconcile --config migration.toml --out docs/reconcile.md
```

至少覆盖：

- 行数；
- 金额/数量汇总；
- 关键业务键抽样；
- 唯一键/外键/空值检查。

### 6. 切换

按 `docs/cutover-checklist.md`：

1. 通知业务停止写入；
2. 记录冻结时间；
3. 跑最终增量；
4. 对账通过；
5. 切换应用连接；
6. 验证健康检查和主链路；
7. 观察 24–72 小时；
8. 源库只读保留，作为回滚兜底。

## 迁移工具

```bash
migration-kit profile  --config migration.toml --out docs/profile.md
migration-kit plan     --config migration.toml
migration-kit run      --config migration.toml            # dry-run
migration-kit run      --config migration.toml --apply    # 写入
migration-kit reconcile --config migration.toml --out docs/reconcile.md
```

常用参数：

- `--limit N`：只处理前 N 行；
- `--batch-size N`：覆盖批次大小；
- `--reset-state`：忽略断点重新开始。

## 映射约定

`mapping.csv`：

```csv
target_column,source_column,target_type,required,default,transform
legacy_id,id,bigint,true,,trim
name,name,text,true,,trim
phone,phone,text,false,,digits
status,status,text,true,active,map_status
```

- `target_type`：text / varchar / int / bigint / numeric / boolean / date / timestamptz / uuid；
- 内置 transform：trim / lower / upper / digits / decimal / bool / date / datetime / uuid / identity；
- 自定义 transform：`transforms.py` 中 `TRANSFORMS = {"name": fn}`；
- 空字符串按 NULL 处理；
- 金额用 numeric/Decimal，不用 float。

## 硬性规则

- 源库只读；禁止在源库建表、改数据。
- `--apply` 前必须有目标库备份，且备份可恢复。
- 默认 dry-run；不允许脚本默认写生产。
- `run.key` 必须对应目标表唯一索引；没有 key 时计划会 WARN，重复执行可能产生重复数据。
- 目标表由应用迁移创建；迁移工具不建表、不删表、不 truncate。
- 配置中的 DSN 用 `${ENV_VAR}`，不把密码写进仓库。
- `on_error=skip` 只用于非关键字段；关键数据用 `stop`。
- 对账未通过不得 cutover。
- 每次正式运行记录 processed / written / skipped / errors 和 state。

## 质量门禁

- 画像完成，异常值已解释；
- `plan` 无 ERROR；
- dry-run 样例字段正确，错误为 0 或有明确处理；
- 正式加载后行数、金额、抽样对账通过；
- 断点续跑验证过；
- 目标备份可恢复；
- 切换清单签字；
- 迁移计划、对账记录、切换记录已更新。

## 资源索引

### references（按需加载）

- `references/playbook.md`：完整阶段、角色、门禁与时间线。
- `references/profiling.md`：画像指标、SQL 模板、数据质量检查。
- `references/mapping.md`：字段映射、类型、转换、ID/状态/日期/金额规则。
- `references/loading.md`：批量加载、upsert、断点、性能与错误处理。
- `references/reconciliation.md`：数量/金额/校验和/抽样对账与签字。
- `references/cutover.md`：冻结、最终增量、切换、监控与回滚。
- `references/troubleshooting.md`：编码、日期、重复、外键、慢加载、锁与权限。

### assets

- `assets/kit/`：Python 迁移工具（profile / plan / run / reconcile，含测试）。
- `assets/template/`：迁移工作区模板（migration.toml、mapping.csv、transforms.py、样例数据）。
- `assets/docs-templates/`：migration-plan / reconciliation / cutover-checklist。

### scripts

- `scripts/scaffold.py`：生成迁移工作区与 docs。

## 不要做的事

- 不要在未备份的目标库上 `--apply`；
- 不要写源库；
- 不要让迁移工具自动建表/删表/truncate；
- 不要用 float 处理金额；
- 不要忽略 skipped 行；
- 不要在对账未通过时切换；
- 不要把 DSN 密码写进 `migration.toml`；
- 不要把一次性迁移脚本当成长期同步方案。
