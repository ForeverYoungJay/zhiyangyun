<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>B3 运营看板闭环</h2>
        <div class="desc">聚合床位占用、营收、护理质量与家属满意度，辅助院内运营决策。</div>
      </div>
      <el-button @click="load">刷新看板</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="10">
        <el-card class="zy-card">
          <template #header>运营指标快照</template>
          <el-descriptions :column="1" border v-if="summary">
            <el-descriptions-item label="日期">{{ summary.date }}</el-descriptions-item>
            <el-descriptions-item label="床位占用率">{{ summary.occupancy_rate }}%</el-descriptions-item>
            <el-descriptions-item label="今日营收">{{ summary.today_revenue }}</el-descriptions-item>
            <el-descriptions-item label="完成任务数">{{ summary.completed_tasks }}</el-descriptions-item>
            <el-descriptions-item label="监督均分">{{ summary.avg_supervise_score }}</el-descriptions-item>
            <el-descriptions-item label="家属满意度">{{ summary.survey_avg }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>看板手工补录（历史）</div>
              <div style="font-size:12px;color:#909399">用于补录历史指标：日期、占用率、营收、告警数。</div>
            </div>
          </template>
          <el-form inline>
            <el-form-item label="日期"><el-input v-model="form.metric_date" placeholder="YYYY-MM-DD"/></el-form-item>
            <el-form-item label="占用率(%)"><el-input-number v-model="form.occupancy_rate" :min="0" :max="100"/></el-form-item>
            <el-form-item label="营收"><el-input-number v-model="form.revenue" :min="0"/></el-form-item>
            <el-form-item label="告警数"><el-input-number v-model="form.alerts" :min="0"/></el-form-item>
            <el-button type="primary" @click="createMetric">新增</el-button>
          </el-form>
          <el-table :data="metrics" border style="margin-top:10px">
            <el-table-column prop="metric_date" label="日期"/>
            <el-table-column prop="occupancy_rate" label="占用率"/>
            <el-table-column prop="revenue" label="营收"/>
            <el-table-column prop="alerts" label="告警"/>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const summary = ref<any>(null)
const metrics = ref<any[]>([])
const form = reactive({ metric_date: new Date().toISOString().slice(0, 10), occupancy_rate: 0, revenue: 0, alerts: 0 })

const load = async () => {
  summary.value = (await http.get('/b3-dashboard/performance-summary')).data.data
  metrics.value = (await http.get('/b3-dashboard/metrics')).data.data
}

const createMetric = async () => {
  if (!form.metric_date) return ElMessage.error('请填写日期')
  await http.post('/b3-dashboard/metrics', form)
  ElMessage.success('历史指标新增成功')
  await load()
}

onMounted(load)
</script>
