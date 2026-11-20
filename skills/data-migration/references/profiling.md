# 源数据画像

## 1. 必看指标

| 指标 | 为什么 |
|---|---|
| 总行数 | 工作量、批次、时间估算 |
| 主键唯一性 | 目标唯一键/幂等 upsert 的前提 |
| 空值/空字符串 | 必填、默认值、未知值处理 |
| 重复业务键 | 映射到唯一键时会冲突 |
| 枚举/状态分布 | 状态映射是否完整 |
| 日期范围/非法日期 | 时区、格式、0000-00-00 |
| 金额范围/负值/精度 | 数据类型、汇总对账 |
| 外键孤儿 | 迁移顺序、约束冲突 |
| 编码/特殊字符 | 乱码、截断、emoji |
| 超长字段 | 目标 varchar 长度 |

## 2. 工具画像

```bash
migration-kit profile --config migration.toml --out docs/profile.md
migration-kit profile --config migration.toml --limit 10000
```

输出包含行数、空值、空字符串、去重值、样例。

## 3. SQL 模板

### 行数与空值

```sql
SELECT
  count(*) AS total,
  count(*) FILTER (WHERE name IS NULL OR btrim(name) = '') AS name_empty,
  count(*) FILTER (WHERE phone IS NULL OR btrim(phone) = '') AS phone_empty
FROM legacy_customers;
```

MySQL：

```sql
SELECT
  COUNT(*) AS total,
  SUM(name IS NULL OR TRIM(name) = '') AS name_empty
FROM legacy_customers;
```

### 重复业务键

```sql
SELECT business_key, count(*) AS cnt
FROM legacy_customers
GROUP BY business_key
HAVING count(*) > 1
ORDER BY cnt DESC
LIMIT 50;
```

### 状态分布

```sql
SELECT status, count(*) AS cnt
FROM legacy_customers
GROUP BY status
ORDER BY cnt DESC;
```

### 日期/金额范围

```sql
SELECT
  min(created_at) AS min_created,
  max(created_at) AS max_created,
  min(amount) AS min_amount,
  max(amount) AS max_amount,
  sum(amount) AS sum_amount
FROM legacy_orders;
```

### 外键孤儿

```sql
SELECT count(*)
FROM legacy_orders o
LEFT JOIN legacy_customers c ON c.id = o.customer_id
WHERE c.id IS NULL;
```

## 4. CSV / Excel 注意事项

- 编码：UTF-8 / GBK；先用小样本确认；
- 分隔符：逗号、制表符、分号；
- 引号与换行：字段内换行需要正确 quote；
- Excel：合并单元格、隐藏行、公式、日期序列号；
- 表头：空格、BOM、重复列名；
- 空值：空字符串、`NULL`、`N/A`、`-` 需要统一规则。

## 5. 画像报告检查

- [ ] 行数与业务预期一致；
- [ ] 主键/业务键无重复，或重复已解释；
- [ ] 空值/空字符串在可接受范围；
- [ ] 状态枚举都有映射；
- [ ] 日期范围合理，无非法日期；
- [ ] 金额汇总与业务报表能对上；
- [ ] 外键孤儿有处理方案；
- [ ] 编码/特殊字符已抽样确认。
