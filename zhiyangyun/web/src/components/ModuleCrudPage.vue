<template>
  <el-card>
    <template #header>{{ title }}</template>
    <el-form :inline="true" @submit.prevent="createItem">
      <el-form-item v-for="field in fields" :key="field.key" :label="field.label">
        <el-input v-model="form[field.key]" :placeholder="field.placeholder || field.label" />
      </el-form-item>
      <el-button type="primary" @click="createItem">新增</el-button>
    </el-form>
    <el-table :data="items" style="margin-top: 12px" border>
      <el-table-column v-for="col in columns" :key="col" :prop="col" :label="col" min-width="120" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import http from '../api/http'

interface FieldDef { key: string; label: string; placeholder?: string }
const props = defineProps<{ title: string; listUrl: string; createUrl: string; fields: FieldDef[]; columns: string[] }>()

const items = ref<any[]>([])
const form = reactive<Record<string, any>>({})
props.fields.forEach((f) => (form[f.key] = ''))

const load = async () => {
  const resp = await http.get(props.listUrl)
  items.value = resp.data.data || []
}

const createItem = async () => {
  await http.post(props.createUrl, form)
  await load()
}

onMounted(load)
</script>
