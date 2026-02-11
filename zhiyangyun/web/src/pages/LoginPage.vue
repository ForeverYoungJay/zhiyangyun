<template>
  <div style="height:100vh;display:flex;justify-content:center;align-items:center;background:linear-gradient(160deg,#eef3ff 0%,#f9fbff 45%,#f5f7fb 100%)">
    <el-card class="zy-card" style="width:400px">
      <template #header>
        <div style="text-align:center">
          <div style="font-size:20px;font-weight:700;color:#2f6bff">智慧养老运营平台</div>
          <div style="font-size:12px;color:#909399;margin-top:4px">请输入管理员账号登录（默认测试账号见 README）</div>
        </div>
      </template>
      <el-form :model="form" label-position="top" @submit.prevent>
        <el-form-item label="用户名"><el-input v-model="form.username" placeholder="请输入用户名" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" show-password type="password" placeholder="请输入密码" /></el-form-item>
        <el-button :loading="loading" type="primary" style="width:100%" @click="submit">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'Admin@123456' })

const submit = async () => {
  try {
    loading.value = true
    const resp = await http.post('/auth/login', form)
    localStorage.setItem('token', resp.data.data.access_token)
    ElMessage.success('登录成功，欢迎回来')
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}
</script>
