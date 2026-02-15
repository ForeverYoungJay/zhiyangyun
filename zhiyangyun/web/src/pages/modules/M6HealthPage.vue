<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A1-M6 健康档案</h2>
        <div class="desc">生命体征异常规则 + 评估闭环 + 与任务/告警联动，支持分页搜索、长者联想与姓名展示。</div>
      </div>
      <el-space>
        <el-button @click="loadAll">刷新</el-button>
        <el-button type="primary" @click="vitalDrawer = true">录入生命体征</el-button>
        <el-button type="success" @click="assessmentDrawer = true">新增健康评估</el-button>
      </el-space>
    </div>

    <el-alert type="warning" :closable="false" show-icon>
      <template #title>业务规则</template>
      <div>• 体征异常自动触发“健康随访”任务与告警；• 高风险评估自动生成闭环任务；• 评估处理后可一键闭环。</div>
    </el-alert>

    <el-card class="zy-card">
      <template #header>生命体征记录</template>
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="vitalQuery.keyword" placeholder="姓名/编号/异常说明" clearable @change="searchVitals" />
        </el-form-item>
        <el-form-item label="异常级别">
          <el-select v-model="vitalQuery.abnormal_level" clearable placeholder="全部" style="width: 160px" @change="searchVitals">
            <el-option label="normal" value="normal" />
            <el-option label="warning" value="warning" />
            <el-option label="critical" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-table :data="vitals" border>
        <el-table-column prop="elder_name" label="长者姓名" min-width="120" />
        <el-table-column prop="elder_no" label="长者编号" min-width="130" />
        <el-table-column prop="temperature" label="体温" min-width="90" />
        <el-table-column prop="systolic" label="收缩压" min-width="90" />
        <el-table-column prop="diastolic" label="舒张压" min-width="90" />
        <el-table-column prop="pulse" label="脉搏" min-width="90" />
        <el-table-column prop="abnormal_level" label="级别" min-width="100">
          <template #default="scope"><el-tag :class="statusTagClass(scope.row.abnormal_level)">{{ scope.row.abnormal_level || '—' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="abnormal_reason" label="异常说明" min-width="180" />
        <el-table-column prop="recorded_at" label="记录时间" min-width="170" />
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="vitalQuery.page" v-model:page-size="vitalQuery.page_size" :total="vitalTotal" layout="total, sizes, prev, pager, next" @current-change="loadVitals" @size-change="searchVitals" />
      </div>
    </el-card>

    <el-card class="zy-card" style="margin-top:16px">
      <template #header>健康评估（闭环）</template>
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="assessmentQuery.keyword" placeholder="姓名/编号/风险等级" clearable @change="searchAssessments" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="assessmentQuery.status" clearable placeholder="全部" style="width: 160px" @change="searchAssessments">
            <el-option label="open" value="open" />
            <el-option label="closed" value="closed" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-table :data="assessments" border>
        <el-table-column prop="elder_name" label="长者姓名" min-width="120" />
        <el-table-column prop="elder_no" label="长者编号" min-width="130" />
        <el-table-column prop="assessed_on" label="评估日期" min-width="120" />
        <el-table-column prop="adl_score" label="ADL" min-width="80" />
        <el-table-column prop="mmse_score" label="MMSE" min-width="90" />
        <el-table-column prop="risk_level" label="风险等级" min-width="100" />
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status || '—' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="close_note" label="闭环说明" min-width="180" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="scope">
            <el-button v-if="scope.row.status !== 'closed'" type="primary" link @click="closeAssessment(scope.row)">闭环完成</el-button>
            <span v-else style="color:#909399">已闭环</span>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="assessmentQuery.page" v-model:page-size="assessmentQuery.page_size" :total="assessmentTotal" layout="total, sizes, prev, pager, next" @current-change="loadAssessments" @size-change="searchAssessments" />
      </div>
    </el-card>

    <el-drawer v-model="vitalDrawer" title="录入生命体征" size="500px" destroy-on-close>
      <el-form ref="vitalFormRef" :model="vitalForm" :rules="vitalRules" label-width="100px">
        <el-form-item label="长者" prop="elder_id">
          <el-autocomplete v-model="elderKeyword" :fetch-suggestions="queryElders" value-key="label" placeholder="输入姓名/编号搜索" @select="onElderSelectVital" style="width:100%" clearable />
          <div style="font-size:12px;color:#909399;margin-top:4px">已选：{{ selectedElderName || '未选择' }}</div>
        </el-form-item>
        <el-form-item label="体温" prop="temperature"><el-input-number v-model="vitalForm.temperature" :min="30" :max="45" style="width:100%" /></el-form-item>
        <el-form-item label="收缩压" prop="systolic"><el-input-number v-model="vitalForm.systolic" :min="60" :max="260" style="width:100%" /></el-form-item>
        <el-form-item label="舒张压" prop="diastolic"><el-input-number v-model="vitalForm.diastolic" :min="40" :max="180" style="width:100%" /></el-form-item>
        <el-form-item label="脉搏" prop="pulse"><el-input-number v-model="vitalForm.pulse" :min="20" :max="220" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createVital">提交</el-button></template>
    </el-drawer>

    <el-drawer v-model="assessmentDrawer" title="新增健康评估" size="500px" destroy-on-close>
      <el-form ref="assessmentFormRef" :model="assessmentForm" :rules="assessmentRules" label-width="100px">
        <el-form-item label="长者" prop="elder_id">
          <el-autocomplete v-model="assessmentElderKeyword" :fetch-suggestions="queryElders" value-key="label" placeholder="输入姓名/编号搜索" @select="onElderSelectAssessment" style="width:100%" clearable />
        </el-form-item>
        <el-form-item label="评估日期" prop="assessed_on"><el-date-picker v-model="assessmentForm.assessed_on" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="ADL" prop="adl_score"><el-input-number v-model="assessmentForm.adl_score" :min="0" :max="100" style="width:100%" /></el-form-item>
        <el-form-item label="MMSE" prop="mmse_score"><el-input-number v-model="assessmentForm.mmse_score" :min="0" :max="30" style="width:100%" /></el-form-item>
        <el-form-item label="风险等级" prop="risk_level">
          <el-select v-model="assessmentForm.risk_level" style="width:100%">
            <el-option label="low" value="low" />
            <el-option label="medium" value="medium" />
            <el-option label="high" value="high" />
            <el-option label="critical" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createAssessment">提交</el-button></template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const vitals = ref<any[]>([])
const assessments = ref<any[]>([])
const vitalTotal = ref(0)
const assessmentTotal = ref(0)
const vitalDrawer = ref(false)
const assessmentDrawer = ref(false)
const vitalFormRef = ref<FormInstance>()
const assessmentFormRef = ref<FormInstance>()
const elderKeyword = ref('')
const assessmentElderKeyword = ref('')
const selectedElderName = ref('')

const vitalQuery = reactive({ page: 1, page_size: 10, keyword: '', abnormal_level: '' })
const assessmentQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const vitalForm = reactive({ elder_id: '', temperature: 36.5, systolic: 120, diastolic: 80, pulse: 75 })
const assessmentForm = reactive({ elder_id: '', assessed_on: '', adl_score: 60, mmse_score: 24, risk_level: 'medium' })

const vitalRules: FormRules = {
  elder_id: [{ required: true, message: '请选择长者', trigger: 'change' }],
  temperature: [{ required: true, message: '请填写体温', trigger: 'change' }],
  systolic: [{ required: true, message: '请填写收缩压', trigger: 'change' }],
  diastolic: [{ required: true, message: '请填写舒张压', trigger: 'change' }],
  pulse: [{ required: true, message: '请填写脉搏', trigger: 'change' }]
}

const assessmentRules: FormRules = {
  elder_id: [{ required: true, message: '请选择长者', trigger: 'change' }],
  assessed_on: [{ required: true, message: '请选择评估日期', trigger: 'change' }],
  adl_score: [{ required: true, message: '请填写ADL', trigger: 'change' }],
  mmse_score: [{ required: true, message: '请填写MMSE', trigger: 'change' }],
  risk_level: [{ required: true, message: '请选择风险等级', trigger: 'change' }]
}

const loadVitals = async () => {
  const resp = await http.get('/m6-health/vitals', { params: vitalQuery })
  const data = resp.data.data || {}
  vitals.value = data.items || []
  vitalTotal.value = data.total || 0
}

const loadAssessments = async () => {
  const resp = await http.get('/m6-health/assessments', { params: assessmentQuery })
  const data = resp.data.data || {}
  assessments.value = data.items || []
  assessmentTotal.value = data.total || 0
}

const loadAll = async () => { await Promise.all([loadVitals(), loadAssessments()]) }
const searchVitals = async () => { vitalQuery.page = 1; await loadVitals() }
const searchAssessments = async () => { assessmentQuery.page = 1; await loadAssessments() }

const queryElders = async (keyword: string, cb: (items: any[]) => void) => {
  const resp = await http.get('/m6-health/elders/suggest', { params: { keyword, limit: 20 } })
  const list = (resp.data.data || []).map((x: any) => ({ ...x, value: x.id, label: `${x.name}（${x.elder_no}）` }))
  cb(list)
}

const onElderSelectVital = (item: any) => {
  vitalForm.elder_id = item.id
  elderKeyword.value = item.label
  selectedElderName.value = item.name
}

const onElderSelectAssessment = (item: any) => {
  assessmentForm.elder_id = item.id
  assessmentElderKeyword.value = item.label
}

const createVital = async () => {
  await vitalFormRef.value?.validate()
  await http.post('/m6-health/vitals', vitalForm)
  ElMessage.success('体征已录入，异常会自动联动任务/告警')
  vitalDrawer.value = false
  await loadVitals()
}

const createAssessment = async () => {
  await assessmentFormRef.value?.validate()
  await http.post('/m6-health/assessments', assessmentForm)
  ElMessage.success('评估已录入，高风险会自动触发闭环任务')
  assessmentDrawer.value = false
  await loadAssessments()
}

const closeAssessment = async (row: any) => {
  await ElMessageBox.confirm(`确认闭环 ${row.elder_name} 的评估记录？`, '闭环确认', { type: 'warning' })
  await http.post(`/m6-health/assessments/${row.id}/close`, { note: '前台闭环确认' })
  ElMessage.success('评估已闭环')
  await loadAssessments()
}

const statusTagClass = (status: string) => {
  if (['active', 'completed', 'paid', 'approved', 'admitted', 'normal', 'closed'].includes(status)) return 'zy-tag-success'
  if (['pending', 'reserved', 'draft', 'in_progress', 'warning', 'open'].includes(status)) return 'zy-tag-warning'
  if (['failed', 'rejected', 'cancelled', 'discharged', 'critical'].includes(status)) return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(loadAll)
</script>
