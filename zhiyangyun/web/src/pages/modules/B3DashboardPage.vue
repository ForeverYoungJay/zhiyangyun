<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>B3 运营看板闭环</h2>
        <div class="desc">聚合床位占用、营收、护理质量与家属满意度，支持历史指标联动。</div>
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
            <el-descriptions-item label="告警数">{{ summary.alerts }}</el-descriptions-item>
            <el-descriptions-item label="联动补录日期">{{ summary.manual_metric_date || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>看板手工补录（历史）</div>
              <div style="font-size:12px;color:#909399">支持日期筛选/分页，自动联动总览指标。</div>
            </div>
          </template>
          <el-form inline>
            <el-form-item label="日期"><el-input v-model="form.metric_date" placeholder="YYYY-MM-DD"/></el-form-item>
            <el-form-item label="占用率(%)"><el-input-number v-model="form.occupancy_rate" :min="0" :max="100"/></el-form-item>
            <el-form-item label="营收"><el-input-number v-model="form.revenue" :min="0"/></el-form-item>
            <el-form-item label="告警数"><el-input-number v-model="form.alerts" :min="0"/></el-form-item>
            <el-button type="primary" @click="createMetric">新增</el-button>
          </el-form>
          <el-form inline style="margin-top:8px">
            <el-form-item label="开始"><el-input v-model="query.start_date" placeholder="YYYY-MM-DD" @change="onSearch"/></el-form-item>
            <el-form-item label="结束"><el-input v-model="query.end_date" placeholder="YYYY-MM-DD" @change="onSearch"/></el-form-item>
          </el-form>
          <el-table :data="metrics" border style="margin-top:10px">
            <el-table-column prop="metric_date" label="日期"/>
            <el-table-column prop="occupancy_rate" label="占用率"/>
            <el-table-column prop="revenue" label="营收"/>
            <el-table-column prop="alerts" label="告警"/>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="load" />
          </div>
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
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, start_date: '', end_date: '' })
const form = reactive({ metric_date: new Date().toISOString().slice(0, 10), occupancy_rate: 0, revenue: 0, alerts: 0 })

const load = async () => {
  summary.value = (await http.get('/b3-dashboard/performance-summary')).data.data
  const resp = (await http.get('/b3-dashboard/metrics', { params: query })).data.data || {}
  metrics.value = resp.items || []
  total.value = resp.total || 0
}
const onSearch = async () => { query.page = 1; await load() }
const createMetric = async () => {
  if (!form.metric_date) return ElMessage.error('请填写日期')
  await http.post('/b3-dashboard/metrics', form)
  ElMessage.success('历史指标新增成功')
  await load()
}

onMounted(load)
</script>
