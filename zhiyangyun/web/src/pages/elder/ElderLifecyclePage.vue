<template>
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card>
        <template #header>CRM 线索</template>
        <el-form inline>
          <el-form-item><el-input v-model="lead.name" placeholder="姓名" /></el-form-item>
          <el-form-item><el-input v-model="lead.phone" placeholder="手机号" /></el-form-item>
          <el-form-item><el-input v-model="lead.source_channel" placeholder="渠道" /></el-form-item>
          <el-form-item><el-button type="primary" @click="createLead">新增</el-button></el-form-item>
        </el-form>
        <el-table :data="leads"><el-table-column prop="name" label="姓名"/><el-table-column prop="phone" label="电话"/><el-table-column prop="source_channel" label="渠道"/></el-table>
      </el-card>

      <el-card style="margin-top:16px">
        <template #header>长者建档（评估后）</template>
        <el-form label-width="100px">
          <el-form-item label="关联线索"><el-select v-model="elder.lead_id" clearable style="width:100%"><el-option v-for="l in leads" :key="l.id" :label="l.name" :value="l.id"/></el-select></el-form-item>
          <el-form-item label="长者编号"><el-input v-model="elder.elder_no"/></el-form-item>
          <el-form-item label="姓名"><el-input v-model="elder.name"/></el-form-item>
          <el-form-item label="性别"><el-select v-model="elder.gender" style="width:100%"><el-option label="male" value="male"/><el-option label="female" value="female"/></el-select></el-form-item>
          <el-form-item label="护理等级"><el-input v-model="elder.care_level"/></el-form-item>
          <el-form-item><el-button type="primary" @click="createElder">创建档案</el-button></el-form-item>
        </el-form>
      </el-card>
    </el-col>

    <el-col :span="12">
      <el-card>
        <template #header>在院全周期状态</template>
        <el-table :data="elders" @row-click="pickElder">
          <el-table-column prop="elder_no" label="编号"/>
          <el-table-column prop="name" label="姓名"/>
          <el-table-column prop="status" label="状态"/>
          <el-table-column prop="bed_id" label="床位"/>
        </el-table>
      </el-card>

      <el-card style="margin-top:16px">
        <template #header>入住 / 转床 / 退院</template>
        <el-form label-width="80px">
          <el-form-item label="选中长者"><el-input :model-value="selectedElder?.name || ''" disabled/></el-form-item>
          <el-form-item label="楼栋"><el-select v-model="op.building_id" style="width:100%"><el-option v-for="b in buildings" :key="b.id" :value="b.id" :label="b.name"/></el-select></el-form-item>
          <el-form-item label="楼层"><el-select v-model="op.floor_id" style="width:100%"><el-option v-for="f in floors" :key="f.id" :value="f.id" :label="f.name"/></el-select></el-form-item>
          <el-form-item label="房间"><el-select v-model="op.room_id" style="width:100%"><el-option v-for="r in rooms" :key="r.id" :value="r.id" :label="r.room_no"/></el-select></el-form-item>
          <el-form-item label="床位"><el-select v-model="op.bed_id" style="width:100%"><el-option v-for="b in freeBeds" :key="b.id" :value="b.id" :label="`${b.bed_no} (${b.status})`"/></el-select></el-form-item>
          <el-form-item>
            <el-button type="primary" @click="admit">办理入院</el-button>
            <el-button @click="transfer">床位变更</el-button>
            <el-button type="danger" @click="discharge">办理退院</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const leads = ref<any[]>([])
const elders = ref<any[]>([])
const buildings = ref<any[]>([])
const floors = ref<any[]>([])
const rooms = ref<any[]>([])
const beds = ref<any[]>([])
const selectedElder = ref<any | null>(null)

const lead = reactive({ name: '', phone: '', source_channel: 'online', notes: '' })
const elder = reactive({ lead_id: '', elder_no: '', name: '', gender: 'male', care_level: 'L1' })
const op = reactive({ building_id: '', floor_id: '', room_id: '', bed_id: '' })

const freeBeds = computed(() => beds.value.filter((b) => ["vacant", "reserved"].includes(b.status)))

const refresh = async () => {
  leads.value = (await http.get('/elders/leads')).data.data
  elders.value = (await http.get('/elders')).data.data
  buildings.value = (await http.get('/assets/buildings')).data.data
  floors.value = (await http.get('/assets/floors')).data.data
  rooms.value = (await http.get('/assets/rooms')).data.data
  beds.value = (await http.get('/assets/beds')).data.data
}

const createLead = async () => { await http.post('/elders/leads', lead); lead.name='';lead.phone=''; await refresh() }
const createElder = async () => { await http.post('/elders', elder); elder.elder_no='';elder.name=''; await refresh() }
const pickElder = (row: any) => { selectedElder.value = row }

const admit = async () => {
  if (!selectedElder.value) return ElMessage.error('请先选择长者')
  await http.post(`/elders/${selectedElder.value.id}/admit`, { ...op, admission_date: new Date().toISOString().slice(0,10) })
  await refresh()
}
const transfer = async () => {
  if (!selectedElder.value) return ElMessage.error('请先选择长者')
  await http.post(`/elders/${selectedElder.value.id}/transfer`, op)
  await refresh()
}
const discharge = async () => {
  if (!selectedElder.value) return ElMessage.error('请先选择长者')
  await http.post(`/elders/${selectedElder.value.id}/discharge`, { discharge_date: new Date().toISOString().slice(0,10), note: '正常退院' })
  await refresh()
}

onMounted(refresh)
</script>
