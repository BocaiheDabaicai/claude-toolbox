import { defineEventHandler, setResponseStatus, type H3Event } from 'h3'

export class ApiError extends Error {
  constructor(
    public readonly statusCode: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export interface ApiSuccess<T> {
  code: 200
  message: 'ok'
  data: T
}

export function ok<T>(data: T): ApiSuccess<T> {
  return { code: 200, message: 'ok', data }
}

export function defineApiHandler<T>(
  handler: (event: H3Event) => T | Promise<T>,
) {
  return defineEventHandler(async (event) => {
    try {
      return await handler(event)
    } catch (error) {
      if (error instanceof ApiError) {
        setResponseStatus(event, error.statusCode)
        return {
          code: error.statusCode,
          message: error.message,
          data: null,
          ...(error.details === undefined ? {} : { details: error.details }),
        }
      }
      console.error('[api] unhandled error', error)
      setResponseStatus(event, 500)
      return { code: 500, message: '服务器内部错误', data: null }
    }
  })
}
