<template>
  <el-card>
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
        <div>
          <div style="font-weight:700">{{ title }}</div>
          <div v-if="description" style="font-size:12px;color:#909399;margin-top:4px">{{ description }}</div>
        </div>
        <el-button @click="load">刷新列表</el-button>
      </div>
    </template>

    <el-alert
      v-if="tips?.length"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom:12px"
      :title="tips[0]"
      :description="tips.slice(1).join('；')"
    />

    <el-form label-width="120px" @submit.prevent="createItem">
      <el-row :gutter="12">
        <el-col :span="12" v-for="field in fields" :key="field.key">
          <el-form-item :label="field.label" :required="field.required">
            <template v-if="field.type === 'select'">
              <el-select
                v-model="form[field.key]"
                style="width:100%"
                :placeholder="field.placeholder || `请选择${field.label}`"
                clearable
              >
                <el-option v-for="op in field.options || []" :key="op.value" :label="op.label" :value="op.value" />
              </el-select>
            </template>
            <template v-else-if="field.type === 'number'">
              <el-input-number
                v-model="form[field.key]"
                style="width:100%"
                :min="field.min ?? 0"
                :max="field.max"
                :placeholder="field.placeholder || `请输入${field.label}`"
              />
            </template>
            <template v-else-if="field.type === 'date'">
              <el-date-picker
                v-model="form[field.key]"
                type="date"
                style="width:100%"
                value-format="YYYY-MM-DD"
                :placeholder="field.placeholder || `请选择${field.label}`"
              />
            </template>
            <template v-else>
              <el-input
                v-model="form[field.key]"
                :placeholder="field.placeholder || `请输入${field.label}`"
                :type="field.type === 'textarea' ? 'textarea' : 'text'"
                :rows="field.type === 'textarea' ? 2 : undefined"
                clearable
              />
            </template>
            <div v-if="field.help" style="font-size:12px;color:#909399;margin-top:4px">{{ field.help }}</div>
          </el-form-item>
        </el-col>
      </el-row>
      <div style="display:flex;gap:8px">
        <el-button type="primary" @click="createItem">新增</el-button>
        <el-button @click="resetForm">重置</el-button>
      </div>
    </el-form>

    <el-table :data="items" style="margin-top: 12px" border>
      <el-table-column v-for="col in columns" :key="col.prop" :prop="col.prop" :label="col.label" min-width="120" />
      <template #empty>
        <el-empty description="暂无数据，请先填写上方表单后点击新增" />
      </template>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

interface FieldOption { label: string; value: string | number }
interface FieldDef {
  key: string
  label: string
  placeholder?: string
  help?: string
  required?: boolean
  type?: 'text' | 'number' | 'date' | 'select' | 'textarea'
  options?: FieldOption[]
  min?: number
  max?: number
  defaultValue?: any
}
interface ColumnDef { prop: string; label: string }

const props = defineProps<{
  title: string
  description?: string
  listUrl: string
  createUrl: string
  fields: FieldDef[]
  columns: ColumnDef[]
  tips?: string[]
}>()

const items = ref<any[]>([])
const form = reactive<Record<string, any>>({})

const initForm = () => {
  props.fields.forEach((f) => {
    form[f.key] = f.defaultValue ?? (f.type === 'number' ? 0 : '')
  })
}
initForm()

const load = async () => {
  const resp = await http.get(props.listUrl)
  items.value = resp.data.data || []
}

const resetForm = () => initForm()

const createItem = async () => {
  for (const f of props.fields) {
    if (f.required && (form[f.key] === '' || form[f.key] === null || form[f.key] === undefined)) {
      ElMessage.error(`请先填写：${f.label}`)
      return
    }
  }
  await http.post(props.createUrl, form)
  ElMessage.success('新增成功')
  await load()
  resetForm()
}

onMounted(load)
</script>
