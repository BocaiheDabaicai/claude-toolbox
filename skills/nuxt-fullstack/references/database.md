# 数据库与 Drizzle

## 1. 基本约定

- 一个项目一个独立 database，例如 `app_crm`；
- 表名复数、snake_case；字段 snake_case；
- 主键 `bigserial`；
- 必备审计字段：`created_at`、`updated_at`；
- 需要保留历史时用 `deleted_at` 软删，不做物理删除；
- 每个查询路径按需建索引，不盲目加。

## 2. Schema 示例

```ts
export const customers = pgTable(
  'customers',
  {
    id: bigserial('id', { mode: 'number' }).primaryKey(),
    name: varchar('name', { length: 100 }).notNull(),
    phone: varchar('phone', { length: 32 }),
    status: varchar('status', { length: 16 }).notNull().default('active'),
    createdAt: timestamp('created_at', { withTimezone: true, mode: 'date' })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true, mode: 'date' })
      .notNull()
      .defaultNow(),
    deletedAt: timestamp('deleted_at', { withTimezone: true, mode: 'date' }),
  },
  (table) => [
    index('customers_name_idx').on(table.name),
    index('customers_deleted_at_idx').on(table.deletedAt),
  ],
)
```

- `mode: 'date'` 让 Node 侧拿到 `Date`，JSON 序列化为 ISO 字符串；
- 枚举先用 `varchar` + Zod enum，避免数据库 enum 迁移成本；
- 金额用 `numeric` + big.js/decimal，不用 `float`。

## 3. 迁移

```bash
pnpm db:generate   # schema -> server/database/migrations/*.sql
pnpm db:migrate    # 应用迁移
```

规则：

- 已应用的迁移不修改，只追加；
- 迁移文件提交到仓库；
- 生产迁移由 `opsctl` 的 oneshot 服务执行；
- 迁移失败时 Web 不应启动（`before` + `Requires`）。

## 4. 连接池

`server/utils/db.ts`：

- 单例 `pg.Pool`，`max: 10`；
- dev 下挂到 `globalThis`，避免 HMR 重复建池；
- `connectionTimeoutMillis: 5000`；
- 不在模块顶层执行查询，避免构建/启动阶段连库。

## 5. 查询模式

### 分页 + 搜索

```ts
const conditions: SQL[] = [isNull(customers.deletedAt)]
if (search) {
  conditions.push(or(
    ilike(customers.name, `%${search}%`),
    ilike(customers.phone, `%${search}%`),
  )!)
}
const where = and(...conditions)
```

- 先 `count()` 再查 rows；
- 固定 `orderBy`，避免分页漂移；
- `pageSize` 上限 100；
- 用户输入只作为参数，不拼 SQL 字符串。

### 软删

```ts
await db.update(customers)
  .set({ deletedAt: new Date(), updatedAt: new Date() })
  .where(and(eq(customers.id, id), isNull(customers.deletedAt)))
```

列表、详情、更新、删除都必须带 `isNull(customers.deletedAt)`。

### 事务

多表写入使用：

```ts
await db.transaction(async (tx) => {
  // ...
})
```

## 6. 常见坑

- **客户端引用 Drizzle**：`app/` 里 import `drizzle-orm` 会被边界检查拦截；不要在页面里写 SQL。
- **HMR 重复连接池**：把 pool/db 挂到 `globalThis`（仅 dev）。
- **count 类型**：`db.select({ value: count() })` 的返回值在 strict 模式下可能被视为 `undefined`，用 `countRow?.value ?? 0`。
- **时间显示**：服务端与客户端时区不同会导致 hydration mismatch；统一用 `formatDateTime`，固定 `Asia/Shanghai`。
- **Date 序列化**：`useFetch` 的 SSR payload 可能把 Date 还原为 Date，客户端 `$fetch` 则是字符串；格式化函数要同时接受 `string | Date`。

## 7. 权限与备份

- 项目使用独立数据库角色，只访问自己的库；
- 生产迁移/备份用单独账号，不用超级用户；
- `pg_dump` 按项目备份，恢复流程写入 `docs/runbook.md`；
- 软删数据保留策略需要业务确认。
