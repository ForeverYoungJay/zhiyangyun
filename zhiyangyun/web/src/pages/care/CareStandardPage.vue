<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>M3 服务与护理标准化</h2>
        <div class="desc">项目、套餐、任务生成、扫码执行、监督评分全流程闭环。</div>
      </div>
      <el-button @click="refresh">刷新全量数据</el-button>
    </div>

    <el-alert type="info" :closable="false" show-icon title="操作顺序：项目库→套餐→绑定项目→长者订阅→生成任务→扫码开始/完成→监督评分。" />

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>服务项目库</template>
          <el-form>
            <el-input v-model="item.name" placeholder="项目名" style="margin-bottom:8px"/>
            <el-input v-model="item.category" placeholder="类别" style="margin-bottom:8px"/>
            <el-input-number v-model="item.unit_price" :min="0" style="width:100%;margin-bottom:8px"/>
            <el-input-number v-model="item.duration_min" :min="5" style="width:100%;margin-bottom:8px"/>
            <el-button type="primary" @click="createItem">新增项目</el-button>
          </el-form>
          <el-table :data="items" border style="margin-top:10px">
            <el-table-column prop="name" label="项目"/>
            <el-table-column prop="unit_price" label="价格"/>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>套餐库</template>
          <el-form>
            <el-input v-model="pkg.name" placeholder="套餐名" style="margin-bottom:8px"/>
            <el-select v-model="pkg.period" style="width:100%;margin-bottom:8px">
              <el-option label="每日" value="daily"/>
              <el-option label="每周" value="weekly"/>
            </el-select>
            <el-button type="primary" @click="createPackage">新增套餐</el-button>
          </el-form>
          <el-table :data="packages" @row-click="pickPackage" border style="margin-top:10px">
            <el-table-column prop="name" label="套餐"/>
            <el-table-column prop="period" label="周期"/>
          </el-table>

          <div style="margin-top:10px;font-weight:700">绑定项目到套餐</div>
          <el-select v-model="bind.item_id" style="width:100%;margin-top:8px" placeholder="选择项目"><el-option v-for="i in items" :key="i.id" :label="i.name" :value="i.id"/></el-select>
          <el-input-number v-model="bind.quantity" :min="1" style="width:100%;margin-top:8px"/>
          <el-button type="success" style="margin-top:8px" @click="bindItem">加入套餐</el-button>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>长者套餐与任务监督</template>
          <el-select v-model="sub.elder_id" placeholder="选择长者" style="width:100%;margin-bottom:8px"><el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id"/></el-select>
          <el-select v-model="sub.package_id" placeholder="选择套餐" style="width:100%;margin-bottom:8px"><el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id"/></el-select>
          <el-button type="primary" @click="subscribe">订阅套餐</el-button>

          <el-select v-model="gen.elder_package_id" placeholder="选择订阅" style="width:100%;margin:12px 0"><el-option v-for="s in subs" :key="s.id" :label="`${s.id.slice(0, 6)}-${s.elder_id.slice(0, 6)}`" :value="s.id"/></el-select>
          <el-button type="warning" @click="generate">生成任务</el-button>

          <el-table :data="tasks" style="margin-top:10px" border>
            <el-table-column prop="status" label="状态">
              <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="supervise_score" label="监督分"/>
            <el-table-column label="操作" min-width="220">
              <template #default="scope">
                <el-button link type="primary" @click="scanIn(scope.row.id)">扫码开始</el-button>
                <el-button link type="success" @click="scanOut(scope.row.id)">扫码完成</el-button>
                <el-button link @click="supervise(scope.row.id)">监督评分</el-button>
              </template>
            </el-table-column>
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

const items = ref<any[]>([])
const packages = ref<any[]>([])
const elders = ref<any[]>([])
const beds = ref<any[]>([])
const subs = ref<any[]>([])
const tasks = ref<any[]>([])

const item = reactive({ name: '', category: 'care', unit_price: 50, duration_min: 30 })
const pkg = reactive({ name: '', period: 'daily' })
const bind = reactive({ package_id: '', item_id: '', quantity: 1 })
const sub = reactive({ elder_id: '', package_id: '' })
const gen = reactive({ elder_package_id: '' })

const refresh = async () => {
  items.value = (await http.get('/care/items')).data.data
  packages.value = (await http.get('/care/packages')).data.data
  elders.value = (await http.get('/elders')).data.data
  beds.value = (await http.get('/assets/beds')).data.data
  tasks.value = (await http.get('/care/tasks')).data.data
}

const createItem = async () => {
  if (!item.name) return ElMessage.error('请填写服务项目名称')
  await http.post('/care/items', item)
  item.name = ''
  await refresh()
}
const createPackage = async () => { await http.post('/care/packages', pkg); pkg.name = ''; await refresh() }
const pickPackage = (row: any) => { bind.package_id = row.id }
const bindItem = async () => {
  if (!bind.package_id || !bind.item_id) return ElMessage.error('请先选择套餐和项目')
  await http.post('/care/package-items', bind)
  ElMessage.success('绑定成功')
}
const subscribe = async () => {
  if (!sub.elder_id || !sub.package_id) return ElMessage.error('请选择长者和套餐')
  const resp = await http.post('/care/elder-packages', { ...sub, start_date: new Date().toISOString().slice(0, 10) })
  subs.value.unshift(resp.data.data)
  ElMessage.success('订阅成功')
}
const generate = async () => { await http.post('/care/tasks/generate', { ...gen, scheduled_at: new Date().toISOString() }); await refresh() }
const getTaskBedQr = (taskId: string) => {
  const task = tasks.value.find((t) => t.id === taskId)
  const elder = elders.value.find((e) => e.id === task?.elder_id)
  const bed = beds.value.find((b) => b.id === elder?.bed_id)
  return bed?.qr_code || ''
}

const scanIn = async (id: string) => { await http.post(`/care/tasks/${id}/scan-in`, { qr_value: getTaskBedQr(id) }); await refresh() }
const scanOut = async (id: string) => { await http.post(`/care/tasks/${id}/scan-out`, { qr_value: getTaskBedQr(id) }); await refresh() }
const supervise = async (id: string) => { await http.post(`/care/tasks/${id}/supervise`, { score: 95 }); await refresh() }

const statusTagClass = (status: string) => {
  if (status === 'completed') return 'zy-tag-success'
  if (status === 'pending' || status === 'in_progress') return 'zy-tag-warning'
  if (status === 'cancelled') return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(refresh)
</script>
