import { createHmac, timingSafeEqual } from 'node:crypto'
import {
  deleteCookie,
  getCookie,
  getHeader,
  setCookie,
  type H3Event,
} from 'h3'
import type { SessionUser } from '~~/shared/types/auth'
import { ApiError } from './response'

interface SessionPayload extends SessionUser {
  iat: number
  exp: number
}

const MAX_AGE = 60 * 60 * 24 * 7

function getConfig(event: H3Event) {
  const config = useRuntimeConfig(event)
  const secret = config.sessionSecret
  if (!secret || secret.length < 32) {
    throw new ApiError(
      500,
      'CONFIG_ERROR',
      'NUXT_SESSION_SECRET 未配置或长度不足 32 位',
    )
  }
  return {
    secret,
    cookieName: config.sessionCookieName || 'app_session',
    secure:
      Boolean(config.public.secureCookies) &&
      process.env.NODE_ENV === 'production',
  }
}

function sign(body: string, secret: string): string {
  return createHmac('sha256', secret).update(body).digest('base64url')
}

export function createUserSession(event: H3Event, user: SessionUser): void {
  const { secret, cookieName, secure } = getConfig(event)
  const now = Math.floor(Date.now() / 1000)
  const payload: SessionPayload = { ...user, iat: now, exp: now + MAX_AGE }
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url')
  const token = `${body}.${sign(body, secret)}`

  setCookie(event, cookieName, token, {
    httpOnly: true,
    sameSite: 'lax',
    secure,
    path: '/',
    maxAge: MAX_AGE,
  })
}

export function clearUserSession(event: H3Event): void {
  const config = useRuntimeConfig(event)
  deleteCookie(event, config.sessionCookieName || 'app_session', { path: '/' })
}

export function readUserSession(event: H3Event): SessionUser | null {
  const { secret, cookieName } = getConfig(event)
  const token = getCookie(event, cookieName)
  if (!token) return null

  const [body, signature] = token.split('.')
  if (!body || !signature) return null

  const expected = Buffer.from(sign(body, secret), 'base64url')
  const actual = Buffer.from(signature, 'base64url')
  if (expected.length !== actual.length || !timingSafeEqual(expected, actual)) {
    return null
  }

  try {
    const payload = JSON.parse(
      Buffer.from(body, 'base64url').toString('utf8'),
    ) as SessionPayload
    if (
      typeof payload.id !== 'number' ||
      typeof payload.email !== 'string' ||
      typeof payload.name !== 'string' ||
      typeof payload.role !== 'string' ||
      typeof payload.exp !== 'number' ||
      payload.exp < Math.floor(Date.now() / 1000)
    ) {
      return null
    }
    return {
      id: payload.id,
      email: payload.email,
      name: payload.name,
      role: payload.role === 'operator' ? 'operator' : 'admin',
    }
  } catch {
    return null
  }
}

export function requireUser(event: H3Event): SessionUser {
  const user = event.context.user
  if (!user) {
    throw new ApiError(401, 'UNAUTHORIZED', '请先登录')
  }
  return user
}

export function requireSameOrigin(event: H3Event): void {
  const origin = getHeader(event, 'origin')
  if (!origin) return

  const host = getHeader(event, 'x-forwarded-host') || getHeader(event, 'host')
  try {
    if (!host || new URL(origin).host !== host) {
      throw new ApiError(403, 'CSRF_REJECTED', '请求来源不合法')
    }
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError(403, 'CSRF_REJECTED', '请求来源不合法')
  }
}
