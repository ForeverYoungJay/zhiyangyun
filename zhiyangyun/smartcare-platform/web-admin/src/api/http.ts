import axios from 'axios'

const http = axios.create({ baseURL: 'http://localhost:8000/api/v1' })

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (resp) => {
    const payload = resp.data
    if (payload?.success === false) return Promise.reject(new Error(payload.message || 'error'))
    return payload
  },
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('token')
      location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default http
