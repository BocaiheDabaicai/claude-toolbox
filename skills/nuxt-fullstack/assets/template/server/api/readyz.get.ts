import { sql } from 'drizzle-orm'
import { db } from '../utils/db'

export default defineEventHandler(async (event) => {
  try {
    await db.execute(sql`select 1`)
    return { status: 'ready' }
  } catch (error) {
    console.error('[readyz] database check failed', error)
    setResponseStatus(event, 503)
    return { status: 'not-ready' }
  }
})
