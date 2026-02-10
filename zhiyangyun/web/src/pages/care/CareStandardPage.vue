<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card>
        <template #header>服务项目库</template>
        <el-form>
          <el-input v-model="item.name" placeholder="项目名" style="margin-bottom:8px"/>
          <el-input v-model="item.category" placeholder="类别" style="margin-bottom:8px"/>
          <el-input-number v-model="item.unit_price" :min="0" style="width:100%;margin-bottom:8px"/>
          <el-input-number v-model="item.duration_min" :min="5" style="width:100%;margin-bottom:8px"/>
          <el-button type="primary" @click="createItem">新增项目</el-button>
        </el-form>
        <el-table :data="items"><el-table-column prop="name" label="项目"/><el-table-column prop="unit_price" label="价格"/></el-table>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card>
        <template #header>套餐库</template>
        <el-form>
          <el-input v-model="pkg.name" placeholder="套餐名" style="margin-bottom:8px"/>
          <el-select v-model="pkg.period" style="width:100%;margin-bottom:8px"><el-option label="daily" value="daily"/><el-option label="weekly" value="weekly"/></el-select>
          <el-button type="primary" @click="createPackage">新增套餐</el-button>
        </el-form>
        <el-table :data="packages" @row-click="pickPackage"><el-table-column prop="name" label="套餐"/><el-table-column prop="period" label="周期"/></el-table>
        <div style="margin-top:10px;font-weight:700">绑定项目</div>
        <el-select v-model="bind.item_id" style="width:100%;margin-top:8px"><el-option v-for="i in items" :key="i.id" :label="i.name" :value="i.id"/></el-select>
        <el-input-number v-model="bind.quantity" :min="1" style="width:100%;margin-top:8px"/>
        <el-button type="success" style="margin-top:8px" @click="bindItem">加入套餐</el-button>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card>
        <template #header>老人套餐与任务生成/监督</template>
        <el-select v-model="sub.elder_id" placeholder="选择长者" style="width:100%;margin-bottom:8px"><el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id"/></el-select>
        <el-select v-model="sub.package_id" placeholder="选择套餐" style="width:100%;margin-bottom:8px"><el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id"/></el-select>
        <el-button type="primary" @click="subscribe">订阅套餐</el-button>

        <el-select v-model="gen.elder_package_id" placeholder="选择订阅" style="width:100%;margin:12px 0"><el-option v-for="s in subs" :key="s.id" :label="`${s.id.slice(0,6)}-${s.elder_id.slice(0,6)}`" :value="s.id"/></el-select>
        <el-button type="warning" @click="generate">生成任务</el-button>

        <el-table :data="tasks" style="margin-top:10px">
          <el-table-column prop="status" label="状态"/>
          <el-table-column prop="supervise_score" label="监督分"/>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button link @click="scanIn(scope.row.id)">扫码开始</el-button>
              <el-button link @click="scanOut(scope.row.id)">扫码完成</el-button>
              <el-button link @click="supervise(scope.row.id)">监督评分</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import http from '../../api/http'

const items = ref<any[]>([])
const packages = ref<any[]>([])
const elders = ref<any[]>([])
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
  tasks.value = (await http.get('/care/tasks')).data.data
}

const createItem = async () => { await http.post('/care/items', item); item.name=''; await refresh() }
const createPackage = async () => { await http.post('/care/packages', pkg); pkg.name=''; await refresh() }
const pickPackage = (row: any) => { bind.package_id = row.id }
const bindItem = async () => { await http.post('/care/package-items', bind) }
const subscribe = async () => {
  const resp = await http.post('/care/elder-packages', { ...sub, start_date: new Date().toISOString().slice(0,10) })
  subs.value.unshift(resp.data.data)
}
const generate = async () => { await http.post('/care/tasks/generate', { ...gen, scheduled_at: new Date().toISOString() }); await refresh() }
const scanIn = async (id: string) => { await http.post(`/care/tasks/${id}/scan-in`, { qr_value: 'QR:ROOM:SIMULATED' }); await refresh() }
const scanOut = async (id: string) => { await http.post(`/care/tasks/${id}/scan-out`, { qr_value: 'QR:ROOM:SIMULATED' }); await refresh() }
const supervise = async (id: string) => { await http.post(`/care/tasks/${id}/supervise`, { score: 95 }); await refresh() }

onMounted(refresh)
</script>
