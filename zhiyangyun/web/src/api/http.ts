import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1',
  timeout: 15000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  config.headers['X-Client-Type'] = 'web_admin'
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const normalizeErrorMessage = (error: any) => {
  const data = error?.response?.data
  if (typeof data?.message === 'string' && data.message.trim()) return data.message
  if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail
  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    return data.detail
      .map((item: any) => `${item?.loc?.slice?.(1).join(' / ') || '字段'}：${item?.msg || '输入不合法'}`)
      .join('；')
  }
  if (error?.response?.status === 404) return '请求资源不存在，请确认操作对象是否已被删除'
  if (error?.response?.status === 500) return '系统服务异常，请稍后重试或联系管理员'
  if (error?.code === 'ECONNABORTED') return '请求超时，请检查网络后重试'
  return error?.message || '请求失败，请稍后重试'
}

http.interceptors.response.use(
  (resp) => {
    if (resp.data && resp.data.success === false) {
      return Promise.reject(new Error(resp.data.message || '业务处理失败'))
    }
    if (typeof resp.data?.code === 'number' && resp.data.code !== 0) {
      return Promise.reject(new Error(resp.data.message || '业务处理失败'))
    }
    return resp
  },
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录状态已失效，请重新登录')
      window.location.href = '/login'
      return Promise.reject(err)
    }

    const message = normalizeErrorMessage(err)
    const traceId = err?.response?.data?.trace_id
    ElMessage.error(traceId ? `${message}（追踪ID：${traceId}）` : message)
    return Promise.reject(new Error(message))
  }
)

export default http
