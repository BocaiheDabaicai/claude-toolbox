import { defineApiHandler, ok } from '../../utils/response'
import { requireUser } from '../../utils/session'

export default defineApiHandler(async (event) =>
  ok({ user: requireUser(event) }),
)
