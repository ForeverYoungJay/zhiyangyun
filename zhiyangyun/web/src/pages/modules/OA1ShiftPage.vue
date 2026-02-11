<template>
  <ModuleCrudPage
    title="A2-OA1 排班模板"
    description="先创建班次模板，再在排班模块引用。"
    list-url="/oa1-shift/templates"
    create-url="/oa1-shift/templates"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'name', label: '班次名称', placeholder: '例如：白班/夜班', required: true },
  { key: 'start_time', label: '开始时间', placeholder: '例如：08:00', required: true },
  { key: 'end_time', label: '结束时间', placeholder: '例如：16:00', required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'name', label: '班次名称' },
  { prop: 'start_time', label: '开始' },
  { prop: 'end_time', label: '结束' }
]
</script>
