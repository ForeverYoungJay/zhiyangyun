import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null as any, token: localStorage.getItem('token') || '' }),
  actions: {
    async login(username: string, password: string) {
      const res = await http.post('/auth/login', { username, password })
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('token', this.token)
    },
    async me() {
      const res = await http.get('/auth/me')
      this.user = res.data
      return this.user
    },
    logout() {
      this.user = null
      this.token = ''
      localStorage.removeItem('token')
    },
  },
})
