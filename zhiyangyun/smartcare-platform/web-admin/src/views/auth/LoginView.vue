<template>
  <div style="height:100vh;display:flex;align-items:center;justify-content:center;">
    <el-card style="width:360px;">
      <template #header>登录</template>
      <el-form @submit.prevent="onSubmit">
        <el-form-item label="用户名"><el-input v-model="username"/></el-form-item>
        <el-form-item label="密码"><el-input v-model="password" type="password"/></el-form-item>
        <el-button type="primary" @click="onSubmit" style="width:100%;">登录</el-button>
      </el-form>
      <div style="margin-top:8px;color:#999;">默认：admin / Admin@123</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../../store/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const username = ref('admin')
const password = ref('Admin@123')
const auth = useAuthStore()
const router = useRouter()

const onSubmit = async () => {
  try {
    await auth.login(username.value, password.value)
    router.push('/assets/overview')
  } catch (e: any) {
    ElMessage.error(e?.message || '登录失败')
  }
}
</script>
