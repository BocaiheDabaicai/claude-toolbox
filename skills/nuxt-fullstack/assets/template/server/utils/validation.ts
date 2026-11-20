import { getQuery, readBody, type H3Event } from 'h3'
import type { ZodType } from 'zod'
import { ApiError } from './response'

type Issue = { path: PropertyKey[]; message: string }

function toDetails(error: { issues: Issue[] }) {
  return error.issues.map((issue) => ({
    path: issue.path.join('.'),
    message: issue.message,
  }))
}

export async function readBodySafe<T>(
  event: H3Event,
  schema: ZodType<T>,
): Promise<T> {
  let body: unknown
  try {
    body = await readBody(event)
  } catch {
    throw new ApiError(400, 'INVALID_JSON', '请求体不是合法 JSON')
  }
  const parsed = schema.safeParse(body)
  if (!parsed.success) {
    throw new ApiError(400, 'VALIDATION_ERROR', '请求参数不合法', toDetails(parsed.error))
  }
  return parsed.data
}

export function readQuerySafe<T>(event: H3Event, schema: ZodType<T>): T {
  const parsed = schema.safeParse(getQuery(event))
  if (!parsed.success) {
    throw new ApiError(400, 'VALIDATION_ERROR', '查询参数不合法', toDetails(parsed.error))
  }
  return parsed.data
}
