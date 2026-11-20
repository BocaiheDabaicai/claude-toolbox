import { defineApiHandler, ok } from '../../utils/response'
import { clearUserSession, requireSameOrigin } from '../../utils/session'

export default defineApiHandler(async (event) => {
  requireSameOrigin(event)
  clearUserSession(event)
  return ok({})
})
