# 常见问题

## 中文乱码

- 确认源文件编码：UTF-8 / GBK；
- `source.encoding` 设置正确；
- CSV/Excel 导出时选择 UTF-8；
- 终端显示乱码不等于数据乱码，查目标库实际值。

## 日期转换失败

- 常见格式：`YYYY-MM-DD`、`YYYY/MM/DD`、`YYYYMMDD`；
- 带时间：`YYYY-MM-DD HH:MM:SS`；
- MySQL `0000-00-00` 需要单独处理；
- 时区：naive 时间默认按 UTC，业务有其他约定时在 transform 中显式处理。

## 金额精度

- 用 `numeric` / `Decimal`，不用 float；
- 去掉 `¥`、`,`；
- 负数/退款确认；
- 对账容差用 Decimal 配置。

## 唯一键冲突

- `run.key` 对应目标唯一索引；
- 源业务键重复：先画像，业务确认保留哪条；
- `ON CONFLICT` 会更新非 key 列；
- 没有 key 时重复执行会产生重复数据。

## 目标表不存在

- 迁移工具不建表；
- 先用应用迁移（Alembic/Drizzle）建表；
- 检查 schema/table 配置和搜索路径。

## 外键失败

- 先迁主表，再迁子表；
- 检查旧 ID -> 新 ID 映射；
- 临时禁用约束只用于排查，切换前必须恢复并验证。

## 权限不足

- 源库只读账号；
- 目标库 INSERT/UPDATE 权限；
- 序列/identity 权限；
- `search_path` 与 schema 权限。

## 加载很慢

- 调大 batch_size（500–5000）；
- 检查网络、磁盘、WAL；
- 迁移期间避免业务高峰；
- 目标索引/约束可临时调整，但切换前恢复；
- 大数据量考虑 COPY + 临时表 + upsert。

## 锁等待 / 长事务

- 每批提交，不长时间持有事务；
- 检查目标库锁：`pg_locks`、`pg_stat_activity`；
- 不要在业务高峰跑全量。

## 断点续跑异常

- 检查 `.migration-state.json`；
- CSV/Excel 用 `{"row": N}`；
- 数据库源用 `cursor_column` + `{"cursor": value}`；
- 修改映射后，确认 state 是否需要重置；
- `--reset-state` 会从头开始。

## 跳过的行

- `on_error=skip` 跳过的行不会自动重试；
- 查 `errors` 输出和源数据；
- 修复后重置相关 state 重跑；
- 关键数据用 `on_error=stop`。

## Excel 读取问题

- 合并单元格、隐藏行、公式；
- 用“值”而不是公式；
- 日期可能是 Excel 序列号，需要转换；
- 表头重复/空格；
- 大文件用 CSV 更稳。

## MySQL 读取问题

- 需要 `pymysql`：`uv tool install '.[mysql]'`；
- `0000-00-00` 日期；
- 字符集 `utf8mb4`；
- 大表建议加 `cursor_column` 做 keyset 分页。

## DSN 密码泄露

- 配置用 `${TARGET_DSN}`；
- 不把 `.env` / DSN 提交仓库；
- 日志只显示 redacted DSN（`user:***@host`）；
- 泄露后立即轮换密码。

## 对账不通过

- 先查行数差异：多迁、少迁、源冻结后新增；
- 再查金额：精度、负值、退款、汇总口径；
- 再抽样：字段映射、枚举、日期；
- 记录差异，不要直接“再跑一次”掩盖。
