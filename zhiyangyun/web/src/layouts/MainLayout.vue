<template>
  <el-container style="height: 100vh">
    <el-aside width="240px" style="border-right:1px solid #ebeef5;background:#fff">
      <div style="padding:16px 16px 8px;font-weight:700;color:#2f6bff">智慧养老运营平台</div>
      <div style="padding:0 16px 12px;color:#909399;font-size:12px">A1业务 · A2运营 · B端闭环</div>
      <el-menu router :default-active="activePath" style="border-right:none">
        <el-menu-item index="/">M1 资产与房间</el-menu-item>
        <el-menu-item index="/elders">M2 长者全周期</el-menu-item>
        <el-menu-item index="/care">M3 服务护理</el-menu-item>
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
      <el-header style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-bottom:1px solid #ebeef5">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ breadcrumb }}</el-breadcrumb-item>
        </el-breadcrumb>
        <el-space>
          <el-tag class="zy-tag-info">管理员</el-tag>
          <el-button @click="logout">退出登录</el-button>
        </el-space>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activePath = computed(() => route.path)
const breadcrumb = computed(() => {
  const map: Record<string, string> = {
    '/': 'M1 资产与房间', '/elders': 'M2 长者全周期', '/care': 'M3 服务护理', '/m4': 'A1-M4 用药管理',
    '/m5': 'A1-M5 膳食管理', '/m6': 'A1-M6 健康档案', '/m7': 'A1-M7 费用管理', '/oa1': 'A2-OA1 排班',
    '/oa2': 'A2-OA2 审批', '/oa3': 'A2-OA3 通知', '/oa4': 'A2-OA4 培训', '/b1': 'B1 小程序闭环',
    '/b2': 'B2 家属门户闭环', '/b3': 'B3 运营看板闭环'
  }
  return map[route.path] || '模块页面'
})

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>
