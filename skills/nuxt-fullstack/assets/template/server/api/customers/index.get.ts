import { and, count, desc, ilike, isNull, or, type SQL } from 'drizzle-orm'
import { z } from 'zod'
import { customers } from '~~/server/database/schema'
import { db } from '../../utils/db'
import { defineApiHandler, ok } from '../../utils/response'
import { readQuerySafe } from '../../utils/validation'

const querySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().trim().max(100).default(''),
})

export default defineApiHandler(async (event) => {
  const { page, pageSize, search } = readQuerySafe(event, querySchema)

  const conditions: SQL[] = [isNull(customers.deletedAt)]
  if (search) {
    conditions.push(
      or(
        ilike(customers.name, `%${search}%`),
        ilike(customers.phone, `%${search}%`),
        ilike(customers.company, `%${search}%`),
      )!,
    )
  }
  const where = and(...conditions)

  const [countRow] = await db
    .select({ value: count() })
    .from(customers)
    .where(where)
  const total = countRow?.value ?? 0

  const rows = await db
    .select()
    .from(customers)
    .where(where)
    .orderBy(desc(customers.createdAt))
    .limit(pageSize)
    .offset((page - 1) * pageSize)

  return ok({ rows, total, page, pageSize })
})
