<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>M3 护理项目中心与治理闭环</h2>
        <div class="desc">项目/项目包维护、半年分配、精准计时、查房任务、院长审核与绩效扣分。</div>
      </div>
      <el-button @click="refresh">刷新</el-button>
    </div>

    <el-row :gutter="12" style="margin-bottom:12px;">
      <el-col :span="4"><el-card>待执行：<b>{{ summary.pending_count }}</b></el-card></el-col>
      <el-col :span="4"><el-card>执行中：<b>{{ summary.in_progress_count }}</b></el-card></el-col>
      <el-col :span="4"><el-card>已完成：<b>{{ summary.completed_count }}</b></el-card></el-col>
      <el-col :span="4"><el-card>逾期：<b>{{ summary.overdue_count }}</b></el-card></el-col>
      <el-col :span="4"><el-card>均耗时：<b>{{ summary.avg_execution_seconds }}s</b></el-card></el-col>
      <el-col :span="4"><el-card>自动扣费：<b>{{ summary.auto_billed_count }}</b></el-card></el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>护理项目中心</template>
          <el-input v-model="item.name" placeholder="项目名" style="margin-bottom:8px"/>
          <el-input v-model="item.category" placeholder="类别" style="margin-bottom:8px"/>
          <el-input-number v-model="item.unit_price" :min="0" style="width:100%;margin-bottom:8px"/>
          <el-button type="primary" @click="createItem">新增项目</el-button>
          <el-table :data="items" border style="margin-top:10px">
            <el-table-column prop="name" label="项目"/>
            <el-table-column prop="status" label="状态"/>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button link @click="toggleItem(scope.row)">{{ scope.row.status === 'active' ? '停用' : '启用' }}</el-button>
                <el-button link type="danger" @click="removeItem(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>项目包 + 半年分配</template>
          <el-input v-model="pkg.name" placeholder="项目包名" style="margin-bottom:8px"/>
          <el-select v-model="pkg.period" style="width:100%;margin-bottom:8px">
            <el-option label="每日" value="daily"/>
            <el-option label="每周" value="weekly"/>
          </el-select>
          <el-button type="primary" @click="createPackage">新增项目包</el-button>

          <el-table :data="packages" @row-click="pickPackage" border style="margin-top:10px">
            <el-table-column prop="name" label="项目包"/>
            <el-table-column prop="default_months" label="默认(月)"/>
          </el-table>

          <el-select v-model="bind.item_id" style="width:100%;margin-top:8px" placeholder="选择项目"><el-option v-for="i in items" :key="i.id" :label="i.name" :value="i.id"/></el-select>
          <el-input-number v-model="bind.quantity" :min="1" style="width:100%;margin-top:8px"/>
          <el-button type="success" style="margin-top:8px" @click="bindItem">加入项目包</el-button>

          <el-divider/>
          <el-select v-model="assign.package_id" placeholder="项目包" style="width:100%;margin-bottom:8px"><el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id"/></el-select>
          <el-select v-model="assign.caregiver_id" placeholder="责任护理员" style="width:100%;margin-bottom:8px"><el-option v-for="u in users" :key="u.id" :label="u.real_name" :value="u.id"/></el-select>
          <el-button type="warning" @click="assignPackage">按半年分配</el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>任务执行与治理</template>
          <el-select v-model="sub.elder_id" placeholder="选择长者" style="width:100%;margin-bottom:8px"><el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id"/></el-select>
          <el-select v-model="sub.package_id" placeholder="选择项目包" style="width:100%;margin-bottom:8px"><el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id"/></el-select>
          <el-button type="primary" @click="subscribe">订阅项目包</el-button>

          <el-select v-model="gen.elder_package_id" placeholder="选择订阅" style="width:100%;margin:10px 0"><el-option v-for="s in subs" :key="s.id" :label="s.id.slice(0,8)" :value="s.id"/></el-select>
          <el-button @click="generate">生成任务</el-button>
          <el-button type="danger" @click="dispatchEmergency" style="margin-left:8px">紧急下发</el-button>

          <el-table :data="board" border style="margin-top:10px">
            <el-table-column prop="assigned_to" label="谁在做"/>
            <el-table-column prop="task_type" label="任务"/>
            <el-table-column prop="elapsed_seconds" label="耗时(秒)"/>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="zy-card" style="margin-top:16px">
      <template #header>任务列表（查房 / 上报院长 / 审核扣分）</template>
      <el-button size="small" @click="createRound('nursing_round')">新增护理查房</el-button>
      <el-button size="small" @click="createRound('admin_round')" style="margin-left:8px">新增行政查房</el-button>
      <el-table :data="tasks" border style="margin-top:10px">
        <el-table-column prop="task_type" label="类型"/>
        <el-table-column prop="status" label="状态"/>
        <el-table-column prop="execution_seconds" label="总秒数"/>
        <el-table-column prop="dean_review_status" label="院长审核"/>
        <el-table-column label="操作" min-width="360">
          <template #default="scope">
            <el-button link type="primary" @click="scanIn(scope.row.id)">扫码开始</el-button>
            <el-button link type="success" @click="scanOut(scope.row.id)">扫码完成</el-button>
            <el-button link @click="reportIssue(scope.row.id)">规范检查留档</el-button>
            <el-button link type="warning" @click="deanReview(scope.row.id)">院长审核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const items = ref<any[]>([])
const packages = ref<any[]>([])
const elders = ref<any[]>([])
const users = ref<any[]>([])
const beds = ref<any[]>([])
const subs = ref<any[]>([])
const tasks = ref<any[]>([])
const board = ref<any[]>([])
const summary = ref<any>({ pending_count: 0, in_progress_count: 0, completed_count: 0, overdue_count: 0, avg_execution_seconds: 0, auto_billed_count: 0 })

const item = reactive({ name: '', category: 'care', unit_price: 50, duration_min: 30 })
const pkg = reactive({ name: '', period: 'daily', default_months: 6 })
const bind = reactive({ package_id: '', item_id: '', quantity: 1 })
const sub = reactive({ elder_id: '', package_id: '' })
const gen = reactive({ elder_package_id: '' })
const assign = reactive({ package_id: '', caregiver_id: '' })

const refresh = async () => {
  items.value = (await http.get('/care/items')).data.data
  packages.value = (await http.get('/care/packages')).data.data
  elders.value = (await http.get('/elders')).data.data
  beds.value = (await http.get('/assets/beds')).data.data
  users.value = (await http.get('/care/caregivers')).data.data || []
  tasks.value = (await http.get('/care/tasks')).data.data
  board.value = (await http.get('/care/tasks/board')).data.data
  summary.value = (await http.get('/care/governance-summary')).data.data
}

const createItem = async () => { await http.post('/care/items', item); item.name = ''; await refresh() }
const toggleItem = async (row:any) => { await http.patch(`/care/items/${row.id}/status`, { status: row.status === 'active' ? 'disabled' : 'active' }); await refresh() }
const removeItem = async (id:string) => { await http.delete(`/care/items/${id}`); await refresh() }
const createPackage = async () => { await http.post('/care/packages', pkg); pkg.name = ''; await refresh() }
const pickPackage = (row:any) => { bind.package_id = row.id; assign.package_id = row.id }
const bindItem = async () => { await http.post('/care/package-items', bind); ElMessage.success('绑定成功') }
const assignPackage = async () => {
  if (!assign.package_id || !assign.caregiver_id) return ElMessage.error('请选择项目包与护理员')
  await http.post('/care/package-assignments', { ...assign, start_date: new Date().toISOString().slice(0, 10), months: 6 })
  ElMessage.success('分配完成')
}
const subscribe = async () => {
  const resp = await http.post('/care/elder-packages', { ...sub, start_date: new Date().toISOString().slice(0, 10) })
  subs.value.unshift(resp.data.data)
}
const generate = async () => { await http.post('/care/tasks/generate', { ...gen, scheduled_at: new Date().toISOString() }); await refresh() }
const dispatchEmergency = async () => {
  await http.post('/care/tasks/dispatch', { elder_package_id: gen.elder_package_id, dispatch_type: 'emergency', frequency: 'day', start_at: new Date().toISOString(), custom_times: 1 })
  await refresh()
}

const getTaskBedQr = (taskId: string) => {
  const task = tasks.value.find((t) => t.id === taskId)
  const elder = elders.value.find((e) => e.id === task?.elder_id)
  const bed = beds.value.find((b) => b.id === elder?.bed_id)
  return bed?.qr_code || ''
}

const scanIn = async (id: string) => { await http.post(`/care/tasks/${id}/scan-in`, { qr_value: getTaskBedQr(id) }); await refresh() }
const scanOut = async (id: string) => { await http.post(`/care/tasks/${id}/scan-out`, { qr_value: getTaskBedQr(id) }); await refresh() }
const createRound = async (roundType: string) => {
  if (!elders.value.length || !items.value.length) return
  await http.post('/care/tasks/round', { elder_id: elders.value[0].id, item_id: items.value[0].id, round_type: roundType, scheduled_at: new Date().toISOString() })
  await refresh()
}
const reportIssue = async (id: string) => { await http.post(`/care/tasks/${id}/issues`, { photo_urls: ['https://example.com/check-photo.jpg'], description: '地面有积水，已上报', report_to_dean: true }); await refresh() }
const deanReview = async (id: string) => { await http.post(`/care/tasks/${id}/dean-review`, { approved: true, note: '确认问题属实', deduction_score: 25 }); await refresh() }

onMounted(refresh)
</script>
