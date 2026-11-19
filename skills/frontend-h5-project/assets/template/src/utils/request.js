import axios from 'axios'
import { getToken, removeToken } from '@/utils/auth'
import { toast } from '@/utils/toast'

// 响应结构以当前后端为准；本模板默认兼容：
// - { code, message, data }（自定义 clientApi）
// - { code, msg, rows, total }（RuoYi 风格）
// 其他结构请在下方响应拦截器里集中适配，页面不要各自判断。
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json;charset=utf-8' },
})

function toLogin() {
  removeToken()
  if (!window.location.hash.startsWith('#/login')) {
    window.location.hash = '#/login'
    toast.error('登录状态已过期，请重新登录')
  }
}

service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) config.headers['Access-Token'] = token
    // 其他后端可能使用 Authorization: `Bearer ${token}`
    // TODO: 按目标后端补充 merchantNo / storeId / platform / isWechat / 经纬度等请求头
    return config
  },
  (error) => Promise.reject(error),
)

// 失败默认弹全局 toast；页面自行渲染错误态的场景，在请求配置里传 silent: true 跳过
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (!res || typeof res !== 'object') return res
    if (res.code === undefined) return res

    if (res.code === 1001 || res.code === 401) {
      toLogin()
      return Promise.reject(new Error(res.message || res.msg || '登录状态已过期，请重新登录'))
    }
    if (res.code === 200 && res.status !== 5000) return res

    const message = res.message || res.msg || '请求失败'
    if (!response.config.silent) toast.error(message)
    return Promise.reject(new Error(message))
  },
  (error) => {
    if (error.response?.status === 401) {
      toLogin()
      return Promise.reject(new Error('登录状态已过期，请重新登录'))
    }
    const message =
      error.response?.data?.message || error.response?.data?.msg || error.message || '网络异常'
    if (!error.config?.silent) toast.error(message)
    return Promise.reject(new Error(message))
  },
)

export default service
