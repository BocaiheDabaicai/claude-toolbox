import { and, eq, isNull } from 'drizzle-orm'
import { customers } from '~~/server/database/schema'
import { db } from '../../utils/db'
import { ApiError, defineApiHandler, ok } from '../../utils/response'

export default defineApiHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  if (!Number.isInteger(id) || id <= 0) {
    throw new ApiError(400, 'INVALID_ID', 'ID 不合法')
  }

  const [customer] = await db
    .select()
    .from(customers)
    .where(and(eq(customers.id, id), isNull(customers.deletedAt)))
    .limit(1)

  if (!customer) {
    throw new ApiError(404, 'NOT_FOUND', '客户不存在')
  }
  return ok(customer)
})
