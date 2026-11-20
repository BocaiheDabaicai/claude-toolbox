import type { AsyncData, NuxtError } from 'nuxt/app'
import { isRef, type ComputedRef, type WatchSource } from 'vue'

type QueryValue = string | number | boolean | undefined | null
type Query = Record<string, QueryValue>

export interface ApiFetchOptions {
  query?: Query | ComputedRef<Query>
  watch?: WatchSource<unknown>[]
  key?: string
}

/**
 * SSR 安全的受保护接口请求：
 * - 服务端用 useRequestFetch 转发 Cookie；
 * - 客户端用 $fetch；
 * - 返回值仍是 useAsyncData，支持 pending / error / refresh；
 * - 同一 URL 有多个调用点时传唯一 key，避免 SSR 数据缓存串页。
 */
export function useApiFetch<T>(
  url: string,
  options: ApiFetchOptions = {},
): AsyncData<T, NuxtError> {
  const requestFetch = (import.meta.server ? useRequestFetch() : $fetch) as typeof $fetch
  const fetcher = async (): Promise<T> => {
    const query = isRef(options.query) ? options.query.value : options.query
    // Nuxt 的 $fetch 泛型会经过 TypedInternalResponse 包装，这里收敛为业务声明的 T。
    return (await requestFetch<T>(url, { query })) as unknown as T
  }
  return useAsyncData<T>(options.key ?? `api:${url}`, fetcher, {
    watch: options.watch,
  }) as AsyncData<T, NuxtError>
}
