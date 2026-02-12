<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A1-M4 用药管理</h2>
        <div class="desc">医嘱执行自动联动账单，支持分页检索、长者自动联想与姓名展示。</div>
      </div>
      <el-space>
        <el-button @click="loadOrders">刷新</el-button>
        <el-button type="primary" @click="drawerVisible = true">新建医嘱</el-button>
      </el-space>
    </div>

    <el-alert type="info" :closable="false" show-icon>
      <template #title>流程提示</template>
      <div>• 录入医嘱后可在下方一键执行；• 执行成功会自动写入 M7 账单与当月发票总额；• 同一医嘱同日避免重复执行。</div>
    </el-alert>

    <el-card class="zy-card">
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="query.keyword" clearable placeholder="药品/剂量/长者姓名/编号" style="width: 240px" @change="onSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部状态" style="width: 170px" @change="onSearch">
            <el-option label="active" value="active" />
            <el-option label="stopped" value="stopped" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="orders" border style="margin-top: 8px">
        <el-table-column prop="elder_name" label="长者姓名" min-width="120" />
        <el-table-column prop="elder_no" label="长者编号" min-width="130" />
        <el-table-column prop="drug_name" label="药品" min-width="120" />
        <el-table-column prop="dosage" label="剂量" min-width="100" />
        <el-table-column prop="frequency" label="频次" min-width="100" />
        <el-table-column prop="start_date" label="开始日期" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="scope">
            <el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status || '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="executeOrder(scope.row)">登记执行</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无医嘱" />
        </template>
      </el-table>

      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @current-change="loadOrders"
          @size-change="onSizeChange"
        />
      </div>
    </el-card>

    <el-card class="zy-card" style="margin-top: 16px">
      <template #header>执行记录（最近）</template>
      <el-table :data="executions" border>
        <el-table-column prop="executed_at" label="执行时间" min-width="170" />
        <el-table-column prop="elder_name" label="长者姓名" min-width="110" />
        <el-table-column prop="drug_name" label="药品" min-width="120" />
        <el-table-column prop="result" label="结果" min-width="90" />
        <el-table-column prop="note" label="备注" min-width="180" />
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" title="新建医嘱" size="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="长者" prop="elder_id">
          <el-autocomplete
            v-model="elderKeyword"
            :fetch-suggestions="queryElders"
            value-key="label"
            placeholder="输入姓名/编号搜索长者"
            @select="onElderSelect"
            clearable
            style="width:100%"
          />
          <div style="font-size:12px;color:#909399;margin-top:4px">已选：{{ selectedElderName || '未选择' }}</div>
        </el-form-item>
        <el-form-item label="药品" prop="drug_name"><el-input v-model="form.drug_name" /></el-form-item>
        <el-form-item label="剂量" prop="dosage"><el-input v-model="form.dosage" placeholder="例如 100mg" /></el-form-item>
        <el-form-item label="频次" prop="frequency"><el-input v-model="form.frequency" placeholder="例如 qd / bid" /></el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" @click="createOrder">提交</el-button>
        </el-space>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const orders = ref<any[]>([])
const executions = ref<any[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const formRef = ref<FormInstance>()
const elderKeyword = ref('')
const selectedElderName = ref('')

const query = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const form = reactive({ elder_id: '', drug_name: '', dosage: '100mg', frequency: 'qd', start_date: '' })

const rules: FormRules = {
  elder_id: [{ required: true, message: '请选择长者', trigger: 'change' }],
  drug_name: [{ required: true, message: '请填写药品名称', trigger: 'blur' }],
  dosage: [{ required: true, message: '请填写剂量', trigger: 'blur' }],
  frequency: [{ required: true, message: '请填写频次', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

const loadOrders = async () => {
  const resp = await http.get('/m4-medication/orders', { params: query })
  const data = resp.data.data || {}
  orders.value = data.items || []
  total.value = data.total || 0
}

const loadExecutions = async () => {
  const resp = await http.get('/m4-medication/executions')
  executions.value = (resp.data.data || []).slice(0, 20)
}

const onSearch = async () => {
  query.page = 1
  await loadOrders()
}

const onSizeChange = async () => {
  query.page = 1
  await loadOrders()
}

const queryElders = async (keyword: string, cb: (items: any[]) => void) => {
  const resp = await http.get('/m4-medication/elders/suggest', { params: { keyword, limit: 20 } })
  const list = (resp.data.data || []).map((x: any) => ({ ...x, value: x.id, label: `${x.name}（${x.elder_no}）` }))
  cb(list)
}

const onElderSelect = (item: any) => {
  form.elder_id = item.id
  elderKeyword.value = item.label
  selectedElderName.value = item.name
}

const resetForm = () => {
  form.elder_id = ''
  form.drug_name = ''
  form.dosage = '100mg'
  form.frequency = 'qd'
  form.start_date = ''
  elderKeyword.value = ''
  selectedElderName.value = ''
  formRef.value?.clearValidate()
}

const createOrder = async () => {
  await formRef.value?.validate()
  await http.post('/m4-medication/orders', form)
  ElMessage.success('医嘱已创建')
  drawerVisible.value = false
  await loadOrders()
  resetForm()
}

const executeOrder = async (row: any) => {
  await ElMessageBox.confirm(`确认登记“${row.elder_name} - ${row.drug_name}”执行？`, '执行确认', { type: 'warning' })
  await http.post('/m4-medication/executions', { order_id: row.id, result: 'done', note: '前台登记执行' })
  ElMessage.success('执行成功，已同步账单')
  await Promise.all([loadOrders(), loadExecutions()])
}

const statusTagClass = (status: string) => {
  if (['active', 'completed', 'paid', 'approved', 'admitted'].includes(status)) return 'zy-tag-success'
  if (['pending', 'reserved', 'draft', 'in_progress'].includes(status)) return 'zy-tag-warning'
  if (['failed', 'rejected', 'cancelled', 'discharged', 'stopped'].includes(status)) return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(async () => {
  await Promise.all([loadOrders(), loadExecutions()])
})
</script>
