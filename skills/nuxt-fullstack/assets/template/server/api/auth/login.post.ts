import { eq } from 'drizzle-orm'
import { users } from '~~/server/database/schema'
import { loginSchema } from '~~/shared/schemas/auth'
import { db } from '../../utils/db'
import { verifyPassword } from '../../utils/password'
import { ApiError, defineApiHandler, ok } from '../../utils/response'
import { createUserSession, requireSameOrigin } from '../../utils/session'
import { readBodySafe } from '../../utils/validation'

export default defineApiHandler(async (event) => {
  requireSameOrigin(event)
  const body = await readBodySafe(event, loginSchema)

  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.email, body.email))
    .limit(1)

  if (
    !user ||
    user.status !== 'active' ||
    !verifyPassword(body.password, user.passwordHash)
  ) {
    throw new ApiError(401, 'INVALID_CREDENTIALS', '邮箱或密码不正确')
  }

  const sessionUser = {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role === 'operator' ? ('operator' as const) : ('admin' as const),
  }

  createUserSession(event, sessionUser)
  return ok({ user: sessionUser })
})
