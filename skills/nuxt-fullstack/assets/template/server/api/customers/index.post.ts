import { customers } from '~~/server/database/schema'
import { customerInputSchema } from '~~/shared/schemas/customer'
import { db } from '../../utils/db'
import { defineApiHandler, ok } from '../../utils/response'
import { requireSameOrigin } from '../../utils/session'
import { readBodySafe } from '../../utils/validation'

export default defineApiHandler(async (event) => {
  requireSameOrigin(event)
  const input = await readBodySafe(event, customerInputSchema)
  const [created] = await db.insert(customers).values(input).returning()
  return ok(created)
})
