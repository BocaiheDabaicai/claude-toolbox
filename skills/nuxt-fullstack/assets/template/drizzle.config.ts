import 'dotenv/config'
import { defineConfig } from 'drizzle-kit'

// generate 不需要真实连接；migrate 需要 .env 里的真实地址。
const url =
  process.env.NUXT_DATABASE_URL ||
  process.env.DATABASE_URL ||
  'postgresql://postgres:postgres@127.0.0.1:5432/placeholder'

export default defineConfig({
  schema: './server/database/schema.ts',
  out: './server/database/migrations',
  dialect: 'postgresql',
  dbCredentials: { url },
  strict: true,
  verbose: true,
})
