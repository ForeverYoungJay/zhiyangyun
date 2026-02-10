<template>
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
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-select :model-value="scope.row.status" @change="(v:string)=>updateStatus(scope.row.id,v)" style="width:120px">
                <el-option label="vacant" value="vacant"/><el-option label="reserved" value="reserved"/><el-option label="occupied" value="occupied"/><el-option label="maintenance" value="maintenance"/>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="qr_code" label="二维码值"/>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import http from '../../api/http'

const buildings = ref<any[]>([])
const floors = ref<any[]>([])
const rooms = ref<any[]>([])
const beds = ref<any[]>([])

const building = reactive({ name: '', code: '' })
const floor = reactive({ building_id: '', floor_no: 1, name: '' })
const room = reactive({ building_id: '', floor_id: '', room_no: '', room_type: 'double' })
const bed = reactive({ room_id: '', bed_no: '' })

const refresh = async () => {
  buildings.value = (await http.get('/assets/buildings')).data.data
  floors.value = (await http.get('/assets/floors')).data.data
  rooms.value = (await http.get('/assets/rooms')).data.data
  beds.value = (await http.get('/assets/beds')).data.data
}

const createBuilding = async () => { await http.post('/assets/buildings', building); building.name='';building.code=''; await refresh() }
const createFloor = async () => { await http.post('/assets/floors', floor); floor.name=''; await refresh() }
const createRoom = async () => { await http.post('/assets/rooms', room); room.room_no=''; await refresh() }
const createBed = async () => { await http.post('/assets/beds', bed); bed.bed_no=''; await refresh() }
const updateStatus = async (id: string, status: string) => { await http.patch(`/assets/beds/${id}/status`, { status }); await refresh() }

onMounted(refresh)
</script>
