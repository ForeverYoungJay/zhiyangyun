<template>
  <ModuleCrudPage
    title="A2-OA4 培训课程"
    description="创建课程后可在员工培训记录中引用。"
    list-url="/oa4-training/courses"
    create-url="/oa4-training/courses"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'title', label: '课程名称', required: true },
  {
    key: 'category',
    label: '课程类型',
    type: 'select',
    required: true,
    options: [
      { label: '护理技能', value: 'care' },
      { label: '安全规范', value: 'safety' },
      { label: '制度学习', value: 'policy' }
    ]
  },
  { key: 'required_score', label: '及格分', type: 'number', min: 0, max: 100, required: true, defaultValue: 60 }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'title', label: '课程名称' },
  { prop: 'category', label: '类型' },
  { prop: 'required_score', label: '及格分' },
  { prop: 'status', label: '状态' }
]
</script>
