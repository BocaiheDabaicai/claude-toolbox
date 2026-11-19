// 登录回跳等场景只允许站内路径，避免开放重定向
// 拒绝：//host、http(s)://host、javascript:、含反斜杠的路径
export function safeRedirect(value, fallback = '/') {
  if (typeof value !== 'string') return fallback
  const target = value.trim()
  if (!target.startsWith('/') || target.startsWith('//') || target.includes('\\')) return fallback
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(target)) return fallback
  return target
}
