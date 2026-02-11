<template>
  <ModuleCrudPage
    title="B1 护理员端服务请求"
    description="模拟小程序端提交服务请求/异常上报。"
    list-url="/b1-miniapp/requests"
    create-url="/b1-miniapp/requests"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'elder_id', label: '长者ID', required: true, placeholder: '例如：ELDER UUID' },
  {
    key: 'request_type',
    label: '请求类型',
    type: 'select',
    required: true,
    options: [
      { label: '护理服务', value: 'care' },
      { label: '健康异常', value: 'health_alert' },
      { label: '生活协助', value: 'life_help' }
    ]
  },
  { key: 'content', label: '请求内容', type: 'textarea', required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'elder_id', label: '长者ID' },
  { prop: 'request_type', label: '类型' },
  { prop: 'content', label: '内容' },
  { prop: 'status', label: '状态' }
]
</script>
