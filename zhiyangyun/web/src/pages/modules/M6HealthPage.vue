<template>
  <ModuleCrudPage
    title="A1-M6 健康档案"
    description="记录生命体征，为医护端和看板提供基础数据。"
    list-url="/m6-health/vitals"
    create-url="/m6-health/vitals"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'elder_id', label: '长者ID', placeholder: '例如：5dc33d52-xxxx', required: true },
  { key: 'temperature', label: '体温(℃)', type: 'number', min: 30, max: 45, required: true },
  { key: 'systolic', label: '收缩压(mmHg)', type: 'number', min: 60, max: 260, required: true },
  { key: 'diastolic', label: '舒张压(mmHg)', type: 'number', min: 40, max: 180, required: true },
  { key: 'pulse', label: '脉搏(次/分)', type: 'number', min: 20, max: 220, required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'elder_id', label: '长者ID' },
  { prop: 'temperature', label: '体温' },
  { prop: 'systolic', label: '收缩压' },
  { prop: 'diastolic', label: '舒张压' },
  { prop: 'pulse', label: '脉搏' },
  { prop: 'recorded_at', label: '记录时间' }
]
</script>
