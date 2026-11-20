# 加载

## 1. 基本流程

```
source rows -> transform -> batch -> upsert -> commit -> state
```

- 默认 dry-run；
- `--apply` 才写入；
- 每批提交后更新 state；
- 失败回滚当前批次，修复后从 state 续跑。

## 2. Upsert

```sql
INSERT INTO public.customers (legacy_id, name, phone)
VALUES (%s, %s, %s)
ON CONFLICT (legacy_id)
DO UPDATE SET name = EXCLUDED.name, phone = EXCLUDED.phone;
```

前提：

- `run.key` 对应目标表唯一索引/主键；
- 目标列都存在；
- 不更新 key 列。

没有 key：

- 退化为普通 INSERT；
- 重复执行会产生重复数据；
- `plan` 会 WARN。

## 3. 批次

- 默认 1000 行；
- 大表 500–5000 可调；
- 太小：提交次数多、慢；
- 太大：单批失败回滚成本高、锁时间长；
- 先小批量 dry-run，再压测。

## 4. 断点

- CSV/Excel：`{"row": N}`，从第 N 条数据继续；
- 数据库源：`{"cursor": value}`，需要 `source.cursor_column`（唯一、单调）；
- 失败后先修复数据，再 `--apply`；
- `--reset-state` 才会从头开始；
- 不要手工编辑 state，除非明确知道后果。

## 5. 性能

- 优先批量 `executemany`；
- 更大数据量可考虑 `COPY` 到临时表 + `INSERT ... ON CONFLICT`；
- 迁移前可临时降低目标表索引/约束开销，但必须在切换前恢复并验证；
- 目标库 `maintenance_work_mem`、`wal`、磁盘 IO 会影响速度；
- 监控锁等待和长事务；
- 不要在业务高峰跑全量。

## 6. 错误处理

`on_error`：

- `stop`（推荐）：遇到错误立即停止，修复后从 state 续跑；
- `skip`：记录错误并跳过；**跳过的行不会自动重试**，只适合非关键字段。

错误信息包含行号；修复源数据/映射后重新跑。

## 7. 目标表

- 由应用迁移（Alembic/Drizzle）创建；
- 迁移工具不建表、不删表、不 truncate；
- 目标表需要有：
  - 主键；
  - `run.key` 对应唯一索引；
  - 需要的审计字段；
  - 外键/检查约束。

## 8. 运行记录

保留：

- 命令；
- 开始/结束时间；
- processed / written / skipped / errors；
- state 文件；
- 目标库备份位置。

## 9. 检查清单

- [ ] 目标备份可恢复；
- [ ] `plan` 无 ERROR；
- [ ] dry-run 样例正确；
- [ ] 小批量 `--apply` 成功；
- [ ] 全量加载成功；
- [ ] state 符合预期；
- [ ] 错误为 0 或已处理；
- [ ] 目标表索引/约束已恢复。
