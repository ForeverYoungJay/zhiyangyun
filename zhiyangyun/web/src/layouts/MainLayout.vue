<template>
  <el-container style="height: 100vh">
    <el-aside width="220px">
      <div style="padding:16px;font-weight:700">智慧养老管理门户</div>
      <el-menu router default-active="/">
        <el-menu-item index="/">M1 资产与房间管理</el-menu-item>
        <el-menu-item index="/elders">M2 长者全周期管理</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;justify-content:flex-end;align-items:center">
        <el-button @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>
