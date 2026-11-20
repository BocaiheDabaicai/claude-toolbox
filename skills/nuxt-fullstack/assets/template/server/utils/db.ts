import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'
import * as schema from '~~/server/database/schema'

function createPool(): Pool {
  const config = useRuntimeConfig()
  if (!config.databaseUrl) {
    console.warn('[db] NUXT_DATABASE_URL 未配置，数据库查询将失败')
  }
  return new Pool({
    connectionString: config.databaseUrl || undefined,
    max: 10,
    idleTimeoutMillis: 30_000,
    connectionTimeoutMillis: 5_000,
  })
}

function createDb(pool: Pool) {
  return drizzle(pool, { schema })
}

type Database = ReturnType<typeof createDb>

const globalForDb = globalThis as unknown as {
  __appPool?: Pool
  __appDb?: Database
}

export const pool = globalForDb.__appPool ?? createPool()
export const db = globalForDb.__appDb ?? createDb(pool)

if (process.env.NODE_ENV !== 'production') {
  globalForDb.__appPool = pool
  globalForDb.__appDb = db
}
