// localStorage 键统一加项目前缀，避免同一域名下多项目互相覆盖。
// 脚手架会把 __STORAGE_PREFIX__ 替换为项目名；手工复制模板时必须自行修改。
const PREFIX = '__STORAGE_PREFIX__'
const TOKEN_KEY = `${PREFIX}_token`
const USER_ID_KEY = `${PREFIX}_user_id`

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// 登录/获取用户信息后写入；需要「当前会员 ID」的接口从这里取，禁止由调用方随意传入
export function getUserId() {
  const id = Number(localStorage.getItem(USER_ID_KEY))
  return Number.isFinite(id) && id > 0 ? id : 0
}

export function setUserId(value) {
  if (Number(value) > 0) localStorage.setItem(USER_ID_KEY, String(value))
  else localStorage.removeItem(USER_ID_KEY)
}

export function removeUserId() {
  localStorage.removeItem(USER_ID_KEY)
}
