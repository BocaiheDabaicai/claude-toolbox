import { and, eq, isNull } from 'drizzle-orm'
import { customers } from '~~/server/database/schema'
import { customerInputSchema } from '~~/shared/schemas/customer'
import { db } from '../../utils/db'
import { ApiError, defineApiHandler, ok } from '../../utils/response'
import { requireSameOrigin } from '../../utils/session'
import { readBodySafe } from '../../utils/validation'

export default defineApiHandler(async (event) => {
  requireSameOrigin(event)
  const id = Number(getRouterParam(event, 'id'))
  if (!Number.isInteger(id) || id <= 0) {
    throw new ApiError(400, 'INVALID_ID', 'ID 不合法')
  }

  const input = await readBodySafe(event, customerInputSchema)
  const [updated] = await db
    .update(customers)
    .set({ ...input, updatedAt: new Date() })
    .where(and(eq(customers.id, id), isNull(customers.deletedAt)))
    .returning()

  if (!updated) {
    throw new ApiError(404, 'NOT_FOUND', '客户不存在')
  }
  return ok(updated)
})
