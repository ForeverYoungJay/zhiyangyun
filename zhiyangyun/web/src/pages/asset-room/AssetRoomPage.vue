<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>M1 资产与房间管理</h2>
        <div class="desc">维护楼栋、楼层、房间、床位及二维码，为入院和护理流程提供基础资源。</div>
      </div>
      <div style="display:flex; gap:8px;">
        <el-button @click="refresh">刷新</el-button>
        <el-button type="warning" @click="reconcile">一致性修复</el-button>
      </div>
    </div>

    <el-row :gutter="12" style="margin-bottom:12px;">
      <el-col :span="6"><el-card>总床位：<b>{{ summary.total_beds }}</b></el-card></el-col>
      <el-col :span="6"><el-card>在住床位：<b>{{ summary.occupied_beds }}</b></el-card></el-col>
      <el-col :span="6"><el-card>空床：<b>{{ summary.vacant_beds }}</b></el-card></el-col>
      <el-col :span="6"><el-card>入住率：<b>{{ summary.occupancy_rate }}%</b></el-card></el-col>
    </el-row>

    <el-alert
      v-if="summary.anomaly_count"
      type="warning"
      :closable="false"
      show-icon
      :title="`检测到 ${summary.anomaly_count} 条床位与长者状态不一致，建议执行“一致性修复”`"
      style="margin-bottom:12px"
    />
    <el-alert type="info" :closable="false" show-icon title="操作顺序建议：先创建楼栋→楼层→房间→床位，再通过 M2 入院/转床流程占用床位。" style="margin-bottom:12px" />

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>楼栋</template>
          <el-form inline>
            <el-form-item><el-input v-model="building.name" placeholder="楼栋名" /></el-form-item>
            <el-form-item><el-input v-model="building.code" placeholder="编码" /></el-form-item>
            <el-form-item><el-button type="primary" @click="createBuilding">新增</el-button></el-form-item>
          </el-form>
          <el-table :data="buildings"><el-table-column prop="name" label="名称"/><el-table-column prop="code" label="编码"/></el-table>
        </el-card>
        <el-card style="margin-top:16px">
          <template #header>楼层</template>
          <el-form inline>
            <el-form-item><el-select v-model="floor.building_id" placeholder="楼栋" style="width:120px"><el-option v-for="b in buildings" :key="b.id" :value="b.id" :label="b.name" /></el-select></el-form-item>
            <el-form-item><el-input-number v-model="floor.floor_no" :min="1" /></el-form-item>
            <el-form-item><el-input v-model="floor.name" placeholder="楼层名" /></el-form-item>
            <el-form-item><el-button type="primary" @click="createFloor">新增</el-button></el-form-item>
          </el-form>
          <el-table :data="floors"><el-table-column prop="name" label="楼层"/><el-table-column prop="floor_no" label="层号"/></el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>房间</template>
          <el-form inline>
            <el-form-item><el-select v-model="room.building_id" placeholder="楼栋" style="width:120px"><el-option v-for="b in buildings" :key="b.id" :value="b.id" :label="b.name" /></el-select></el-form-item>
            <el-form-item><el-select v-model="room.floor_id" placeholder="楼层" style="width:120px"><el-option v-for="f in floors" :key="f.id" :value="f.id" :label="f.name" /></el-select></el-form-item>
            <el-form-item><el-input v-model="room.room_no" placeholder="房间号" /></el-form-item>
            <el-form-item><el-select v-model="room.room_type" style="width:120px"><el-option label="single" value="single"/><el-option label="double" value="double"/></el-select></el-form-item>
            <el-form-item><el-button type="primary" @click="createRoom">新增</el-button></el-form-item>
          </el-form>
          <el-table :data="rooms"><el-table-column prop="room_no" label="房间号"/><el-table-column prop="room_type" label="类型"/></el-table>
        </el-card>

        <el-card style="margin-top:16px">
          <template #header>床位 + 二维码文本</template>
          <el-form inline>
            <el-form-item><el-select v-model="bed.room_id" placeholder="房间" style="width:120px"><el-option v-for="r in rooms" :key="r.id" :value="r.id" :label="r.room_no" /></el-select></el-form-item>
            <el-form-item><el-input v-model="bed.bed_no" placeholder="床号" /></el-form-item>
            <el-form-item><el-button type="primary" @click="createBed">新增</el-button></el-form-item>
          </el-form>
          <el-table :data="beds">
            <el-table-column prop="bed_no" label="床号"/>
            <el-table-column prop="status" label="状态" width="160">
              <template #default="scope">
                <el-select :model-value="scope.row.status" @change="(v:string)=>updateStatus(scope.row.id,v)" style="width:130px">
                  <el-option label="vacant" value="vacant"/><el-option label="reserved" value="reserved"/><el-option label="occupied" value="occupied"/><el-option label="maintenance" value="maintenance"/>
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="一致性" width="120">
              <template #default="scope">
                <el-tag :type="bedConsistent(scope.row.id) ? 'success' : 'danger'">{{ bedConsistent(scope.row.id) ? '正常' : '异常' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="qr_code" label="二维码值"/>
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

const buildings = ref<any[]>([])
const floors = ref<any[]>([])
const rooms = ref<any[]>([])
const beds = ref<any[]>([])

const summary = ref<any>({ total_beds: 0, occupied_beds: 0, vacant_beds: 0, occupancy_rate: 0, anomaly_count: 0, anomalies: [] })

const building = reactive({ name: '', code: '' })
const floor = reactive({ building_id: '', floor_no: 1, name: '' })
const room = reactive({ building_id: '', floor_id: '', room_no: '', room_type: 'double' })
const bed = reactive({ room_id: '', bed_no: '' })

const refresh = async () => {
  buildings.value = (await http.get('/assets/buildings')).data.data
  floors.value = (await http.get('/assets/floors')).data.data
  rooms.value = (await http.get('/assets/rooms')).data.data
  beds.value = (await http.get('/assets/beds')).data.data
  summary.value = (await http.get('/assets/occupancy-summary')).data.data
}

const createBuilding = async () => { await http.post('/assets/buildings', building); building.name='';building.code=''; await refresh() }
const createFloor = async () => { await http.post('/assets/floors', floor); floor.name=''; await refresh() }
const createRoom = async () => { await http.post('/assets/rooms', room); room.room_no=''; await refresh() }
const createBed = async () => { await http.post('/assets/beds', bed); bed.bed_no=''; await refresh() }
const updateStatus = async (id: string, status: string) => {
  try {
    await http.patch(`/assets/beds/${id}/status`, { status })
    await refresh()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '状态更新失败')
  }
}
const reconcile = async () => {
  const ret = (await http.post('/assets/beds/reconcile')).data.data
  ElMessage.success(`修复完成：${ret.fixed_count} 条`)
  await refresh()
}

const bedConsistent = (bedId: string) => !summary.value.anomalies?.some((x: any) => x.bed_id === bedId)

onMounted(refresh)
</script>
