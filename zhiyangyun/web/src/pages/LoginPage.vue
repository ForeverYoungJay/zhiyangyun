<template>
  <div style="height:100vh;display:flex;justify-content:center;align-items:center">
    <el-card style="width:360px">
      <template #header>登录</template>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" show-password type="password" /></el-form-item>
        <el-button type="primary" style="width:100%" @click="submit">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const form = reactive({ username: 'admin', password: 'Admin@123456' })

const submit = async () => {
  try {
    const resp = await http.post('/auth/login', form)
    localStorage.setItem('token', resp.data.data.access_token)
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败')
  }
}
</script>
