import 'dotenv/config'
import { count, eq } from 'drizzle-orm'
import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'
import * as schema from '../server/database/schema'
import { hashPassword } from '../server/utils/password'

const url = process.env.NUXT_DATABASE_URL || process.env.DATABASE_URL
if (!url) {
  console.error('[seed] 缺少 NUXT_DATABASE_URL（或 DATABASE_URL）')
  process.exit(1)
}

const email = (process.env.SEED_ADMIN_EMAIL || '').trim().toLowerCase()
const password = process.env.SEED_ADMIN_PASSWORD || ''
const name = process.env.SEED_ADMIN_NAME || '管理员'

if (!email || !password || password.length < 8) {
  console.error(
    '[seed] 请在 .env 中配置 SEED_ADMIN_EMAIL 和至少 8 位的 SEED_ADMIN_PASSWORD',
  )
  process.exit(1)
}

const pool = new Pool({ connectionString: url })
const db = drizzle(pool, { schema })

try {
  const [existing] = await db
    .select()
    .from(schema.users)
    .where(eq(schema.users.email, email))
    .limit(1)

  if (existing) {
    await db
      .update(schema.users)
      .set({
        name,
        passwordHash: hashPassword(password),
        role: 'admin',
        status: 'active',
        updatedAt: new Date(),
      })
      .where(eq(schema.users.id, existing.id))
    console.log(`[seed] 已更新管理员 ${email}`)
  } else {
    await db.insert(schema.users).values({
      email,
      name,
      passwordHash: hashPassword(password),
      role: 'admin',
      status: 'active',
    })
    console.log(`[seed] 已创建管理员 ${email}`)
  }

  const [countRow] = await db
    .select({ value: count() })
    .from(schema.customers)
  const value = countRow?.value ?? 0

  if (value === 0) {
    await db.insert(schema.customers).values([
      {
        name: '张明',
        phone: '13800000001',
        email: 'zhangming@example.com',
        company: '远山科技',
        status: 'active',
        note: '示例数据，可直接删除。',
      },
      {
        name: '李静',
        phone: '13800000002',
        email: 'lijing@example.com',
        company: '青禾贸易',
        status: 'active',
      },
      {
        name: '王强',
        phone: '13800000003',
        company: '恒信物流',
        status: 'inactive',
      },
    ])
    console.log('[seed] 已插入 3 条示例客户')
  } else {
    console.log(`[seed] 已有 ${value} 条客户，跳过示例数据`)
  }
} catch (error) {
  console.error('[seed] 执行失败', error)
  process.exitCode = 1
} finally {
  await pool.end()
}
