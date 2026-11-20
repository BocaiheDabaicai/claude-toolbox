import { defineEventHandler, getRequestURL, setResponseStatus } from 'h3'
import { ApiError } from '../utils/response'
import { readUserSession } from '../utils/session'

const PUBLIC_API = new Set([
  '/api/auth/login',
  '/api/auth/logout',
  '/api/healthz',
  '/api/readyz',
])

export default defineEventHandler((event) => {
  const path = getRequestURL(event).pathname
  if (!path.startsWith('/api/') || PUBLIC_API.has(path)) return

  try {
    const user = readUserSession(event)
    if (!user) {
      setResponseStatus(event, 401)
      return { code: 401, message: '请先登录', data: null }
    }
    event.context.user = user
  } catch (error) {
    setResponseStatus(event, 500)
    const message =
      error instanceof ApiError ? error.message : '会话配置错误'
    return { code: 500, message, data: null }
  }
})
