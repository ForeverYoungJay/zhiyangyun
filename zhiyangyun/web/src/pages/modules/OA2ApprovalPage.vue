<template>
  <ModuleCrudPage
    title="A2-OA2 审批单"
    description="固定审批流：请假/报销/采购。"
    list-url="/oa2-approval/requests"
    create-url="/oa2-approval/requests"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  {
    key: 'module',
    label: '审批类型',
    type: 'select',
    required: true,
    options: [
      { label: '请假', value: 'leave' },
      { label: '报销', value: 'expense' },
      { label: '采购', value: 'purchase' }
    ]
  },
  { key: 'biz_id', label: '业务单号', placeholder: '例如：EXP-20260211-001', required: true },
  { key: 'applicant_id', label: '申请人ID', required: true },
  { key: 'approver_id', label: '审批人ID', required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'module', label: '类型' },
  { prop: 'biz_id', label: '业务单号' },
  { prop: 'applicant_id', label: '申请人' },
  { prop: 'approver_id', label: '审批人' },
  { prop: 'status', label: '状态' }
]
</script>
