<template>
  <ModuleCrudPage
    title="A1-M5 膳食管理"
    description="用于配置每日餐次方案与营养标签。"
    list-url="/m5-meal/plans"
    create-url="/m5-meal/plans"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'name', label: '方案名称', placeholder: '例如：糖尿病低盐餐', required: true },
  { key: 'plan_date', label: '计划日期', type: 'date', required: true },
  {
    key: 'meal_type',
    label: '餐次',
    type: 'select',
    required: true,
    options: [
      { label: '早餐', value: 'breakfast' },
      { label: '午餐', value: 'lunch' },
      { label: '晚餐', value: 'dinner' }
    ]
  },
  { key: 'nutrition_tag', label: '营养标签', placeholder: '低糖/高蛋白/低盐', required: true }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'name', label: '方案名称' },
  { prop: 'plan_date', label: '日期' },
  { prop: 'meal_type', label: '餐次' },
  { prop: 'nutrition_tag', label: '营养标签' }
]
</script>
