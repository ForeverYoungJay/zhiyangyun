<template>
  <ModuleCrudPage
    title="A1-M4 用药管理"
    description="录入医嘱后，可在护理流程中执行并留痕。"
    list-url="/m4-medication/orders"
    create-url="/m4-medication/orders"
    :fields="fields"
    :columns="columns"
    :tips="['elder_id 需填写长者ID（可从长者模块复制）', 'start_date 使用 YYYY-MM-DD']"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'elder_id', label: '长者ID', placeholder: '例如：5dc33d52-xxxx', required: true, help: '从长者列表复制 ID' },
  { key: 'drug_name', label: '药品名称', required: true },
  { key: 'dosage', label: '剂量', placeholder: '例如：5mg', required: true },
  { key: 'frequency', label: '频次', placeholder: '例如：bid / qd', required: true },
  { key: 'start_date', label: '开始日期', type: 'date', required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'elder_id', label: '长者ID' },
  { prop: 'drug_name', label: '药品' },
  { prop: 'dosage', label: '剂量' },
  { prop: 'frequency', label: '频次' },
  { prop: 'start_date', label: '开始日期' },
  { prop: 'status', label: '状态' }
]
</script>
