<template>
  <el-row :gutter="12">
    <el-col :span="6" v-for="item in cards" :key="item.label">
      <el-card>
        <div>{{ item.label }}</div>
        <h2>{{ item.value }}</h2>
      </el-card>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '../../api/http'

const cards = ref([
  { label: '楼栋数', value: 0 },
  { label: '房间数', value: 0 },
  { label: '床位数', value: 0 },
  { label: '空床位', value: 0 },
])

onMounted(async () => {
  const res = await http.get('/assets/overview')
  cards.value = [
    { label: '楼栋数', value: res.data.buildings },
    { label: '房间数', value: res.data.rooms },
    { label: '床位数', value: res.data.beds },
    { label: '空床位', value: res.data.vacant_beds },
  ]
})
</script>
