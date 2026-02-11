<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>{{ title }}</h2>
        <div v-if="description" class="desc">{{ description }}</div>
      </div>
      <el-space>
        <el-button @click="load">刷新</el-button>
        <el-button type="primary" @click="drawerVisible = true">新建记录</el-button>
      </el-space>
    </div>

    <el-alert v-if="tips?.length" type="info" :closable="false" show-icon>
      <template #title>流程提示</template>
      <div>• {{ tips.join('；• ') }}</div>
    </el-alert>

    <el-card class="zy-card">
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="keyword" clearable placeholder="按任意字段搜索" style="width: 220px" />
        </el-form-item>
        <el-form-item label="状态" v-if="hasStatusColumn">
          <el-select v-model="statusFilter" clearable placeholder="全部状态" style="width: 180px">
            <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="pagedItems" border style="margin-top: 8px" @row-click="openDetail">
        <el-table-column v-for="col in columns" :key="col.prop" :prop="col.prop" :label="col.label" min-width="120">
          <template #default="scope" v-if="col.prop === 'status'">
            <el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status || '—' }}</el-tag>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无数据，可点击右上角“新建记录”开始录入" />
        </template>
      </el-table>

      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredItems.length"
        />
      </div>
    </el-card>

    <el-drawer v-model="drawerVisible" title="新建记录" size="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item v-for="field in fields" :key="field.key" :label="field.label" :prop="field.key">
          <template v-if="field.type === 'select'">
            <el-select v-model="form[field.key]" :placeholder="field.placeholder || `请选择${field.label}`" clearable>
              <el-option v-for="op in field.options || []" :key="op.value" :label="op.label" :value="op.value" />
            </el-select>
          </template>
          <template v-else-if="field.type === 'number'">
            <el-input-number v-model="form[field.key]" :min="field.min ?? 0" :max="field.max" style="width:100%" />
          </template>
          <template v-else-if="field.type === 'date'">
            <el-date-picker v-model="form[field.key]" type="date" value-format="YYYY-MM-DD" style="width:100%" />
          </template>
          <template v-else>
            <el-input
              v-model="form[field.key]"
              :placeholder="field.placeholder || `请输入${field.label}`"
              :type="field.type === 'textarea' ? 'textarea' : 'text'"
              :rows="field.type === 'textarea' ? 3 : undefined"
              clearable
            />
          </template>
          <div v-if="field.help" style="font-size:12px;color:#909399;margin-top:4px">{{ field.help }}</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" @click="createItem">提交</el-button>
        </el-space>
      </template>
    </el-drawer>

    <el-drawer v-model="detailVisible" title="详情" size="460px" destroy-on-close>
      <el-descriptions :column="1" border v-if="detailRow">
        <el-descriptions-item v-for="col in columns" :key="col.prop" :label="col.label">
          <el-tag v-if="col.prop === 'status'" :class="statusTagClass(detailRow[col.prop])">{{ detailRow[col.prop] || '—' }}</el-tag>
          <span v-else>{{ detailRow[col.prop] || '—' }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import http from '../api/http'

interface FieldOption { label: string; value: string | number }
interface FieldDef {
  key: string
  label: string
  placeholder?: string
  help?: string
  required?: boolean
  type?: string
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
const keyword = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = ref(10)
const drawerVisible = ref(false)
const detailVisible = ref(false)
const detailRow = ref<any>(null)
const formRef = ref<FormInstance>()

const hasStatusColumn = computed(() => props.columns.some((c) => c.prop === 'status'))
const statusOptions = computed(() => [...new Set(items.value.map((i) => i.status).filter(Boolean))])

const initForm = () => {
  props.fields.forEach((f) => {
    form[f.key] = f.defaultValue ?? (f.type === 'number' ? 0 : '')
  })
}

const rules = computed<FormRules>(() => {
  const all: FormRules = {}
  props.fields.forEach((f) => {
    if (f.required) {
      all[f.key] = [{ required: true, message: `请填写${f.label}`, trigger: 'blur' }]
    }
  })
  return all
})

initForm()

const load = async () => {
  const resp = await http.get(props.listUrl)
  items.value = resp.data.data || []
}

const filteredItems = computed(() => {
  return items.value.filter((row) => {
    const textMatch = !keyword.value || JSON.stringify(row).toLowerCase().includes(keyword.value.toLowerCase())
    const statusMatch = !statusFilter.value || row.status === statusFilter.value
    return textMatch && statusMatch
  })
})

const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredItems.value.slice(start, start + pageSize.value)
})

const resetForm = () => {
  initForm()
  formRef.value?.clearValidate()
}

const createItem = async () => {
  await formRef.value?.validate()
  await http.post(props.createUrl, form)
  ElMessage.success('新增成功')
  drawerVisible.value = false
  await load()
  resetForm()
}

const openDetail = (row: any) => {
  detailRow.value = row
  detailVisible.value = true
}

const statusTagClass = (status: string) => {
  if (!status) return 'zy-tag-info'
  if (['completed', 'paid', 'approved', 'active', 'admitted'].includes(status)) return 'zy-tag-success'
  if (['pending', 'reserved', 'draft', 'in_progress'].includes(status)) return 'zy-tag-warning'
  if (['failed', 'rejected', 'cancelled', 'discharged'].includes(status)) return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(load)
</script>
