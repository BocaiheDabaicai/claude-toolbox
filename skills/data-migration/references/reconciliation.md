# 对账

## 1. 对账层次

| 层次 | 内容 | 是否必须 |
|---|---|---|
| 数量 | 源/目标行数 | 必须 |
| 汇总 | 金额、数量、积分等 sum | 必须 |
| 唯一性 | 主键/业务键重复 | 必须 |
| 空值 | 必填字段空值 | 必须 |
| 外键 | 孤儿记录 | 按业务 |
| 抽样 | 随机/重点记录逐字段 | 必须 |
| 校验和 | 排序后 hash/checksum | 可选 |

## 2. 工具对账

`migration.toml`：

```toml
[[reconcile.checks]]
name = "customers_count"
source_sql = "SELECT count(*) FROM legacy_customers"
target_sql = "SELECT count(*) FROM public.customers"
tolerance = "0"

[[reconcile.checks]]
name = "orders_amount"
source_sql = "SELECT coalesce(sum(amount), 0) FROM legacy_orders"
target_sql = "SELECT coalesce(sum(amount), 0) FROM public.orders"
tolerance = "0.01"
```

运行：

```bash
migration-kit reconcile --config migration.toml --out docs/reconcile.md
```

- 数值按 Decimal 比较，支持容差；
- 非数值按字符串比较；
- 任一 FAIL 退出码为 1；
- SQL 对账只支持 postgres / mysql 源。

## 3. SQL 模板

### 数量

```sql
SELECT count(*) FROM legacy_customers;
SELECT count(*) FROM public.customers;
```

### 金额

```sql
SELECT coalesce(sum(amount), 0) FROM legacy_orders;
SELECT coalesce(sum(amount), 0) FROM public.orders;
```

### 唯一键重复

```sql
SELECT legacy_id, count(*)
FROM public.customers
GROUP BY legacy_id
HAVING count(*) > 1;
```

### 必填空值

```sql
SELECT count(*)
FROM public.customers
WHERE name IS NULL OR btrim(name) = '';
```

### 外键孤儿

```sql
SELECT count(*)
FROM public.orders o
LEFT JOIN public.customers c ON c.id = o.customer_id
WHERE c.id IS NULL;
```

## 4. 抽样

- 随机抽 20–100 条；
- 另抽重点客户/大额订单/异常状态；
- 逐字段比较：名称、电话、邮箱、状态、日期、金额；
- 差异记录业务键、字段、源值、目标值、原因。

## 5. 容差

- 行数：0；
- 金额：按业务精度，通常 0.01；
- 时间：按业务允许的秒级差异；
- 浮点/汇率类：明确说明，不用“看起来差不多”。

## 6. 差异处理

| 类型 | 处理 |
|---|---|
| 源数据错误 | 业务确认后修正源/目标，重跑 |
| 映射错误 | 改 mapping/transform，重置相关 state 重跑 |
| 目标约束 | 修数据或调整目标 schema |
| 可接受差异 | 记录原因，业务签字 |

不要用“再跑一次”掩盖差异；每次重跑都要说明范围和原因。

## 7. 签字

- 数量通过；
- 金额/汇总通过；
- 抽样通过；
- 差异已处理或确认；
- 业务负责人签字。

## 8. 切换后监控

- 应用错误率；
- 关键查询/报表；
- 新增数据是否正常写入；
- 源库是否仍有写入；
- 24–72 小时后确认下线。
