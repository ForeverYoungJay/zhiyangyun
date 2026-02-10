<template>
  <el-container style="height: 100vh">
    <el-aside width="220px">
      <div style="padding:16px;font-weight:700">智慧养老管理门户</div>
      <el-menu router default-active="/">
        <el-menu-item index="/">M1 资产与房间管理</el-menu-item>
        <el-menu-item index="/elders">M2 长者全周期管理</el-menu-item>
        <el-menu-item index="/care">M3 服务与护理标准化</el-menu-item>
        <el-menu-item index="/m4">A1-M4 用药管理</el-menu-item>
        <el-menu-item index="/m5">A1-M5 膳食管理</el-menu-item>
        <el-menu-item index="/m6">A1-M6 健康档案</el-menu-item>
        <el-menu-item index="/m7">A1-M7 费用管理</el-menu-item>
        <el-menu-item index="/oa1">A2-OA1 排班</el-menu-item>
        <el-menu-item index="/oa2">A2-OA2 审批</el-menu-item>
        <el-menu-item index="/oa3">A2-OA3 通知</el-menu-item>
        <el-menu-item index="/oa4">A2-OA4 培训</el-menu-item>
        <el-menu-item index="/b1">B1 小程序闭环</el-menu-item>
        <el-menu-item index="/b2">B2 家属门户闭环</el-menu-item>
        <el-menu-item index="/b3">B3 运营看板闭环</el-menu-item>
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
