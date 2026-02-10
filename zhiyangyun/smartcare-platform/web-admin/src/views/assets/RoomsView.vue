<template>
  <el-space direction="vertical" fill>
    <el-card>
      <el-form inline>
        <el-form-item label="楼栋ID"><el-input v-model="form.building_id" style="width:220px"/></el-form-item>
        <el-form-item label="楼层ID"><el-input v-model="form.floor_id" style="width:220px"/></el-form-item>
        <el-form-item label="房号"><el-input v-model="form.room_no"/></el-form-item>
        <el-form-item label="类型"><el-input v-model="form.room_type"/></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="form.capacity" :min="1"/></el-form-item>
        <el-button type="primary" @click="create">新增</el-button>
      </el-form>
    </el-card>
    <el-card><el-table :data="rows"><el-table-column prop="room_no" label="房号"/><el-table-column prop="room_type" label="类型"/><el-table-column prop="capacity" label="容量"/><el-table-column prop="status" label="状态"/></el-table></el-card>
  </el-space>
</template>
<script setup lang="ts">
import { ref,onMounted } from 'vue';import http from '../../api/http';
const rows=ref<any[]>([]);const form=ref({building_id:'',floor_id:'',room_no:'',room_type:'双人间',capacity:2})
const load=async()=>{rows.value=(await http.get('/rooms')).data}
const create=async()=>{await http.post('/rooms',form.value);await load()}
onMounted(load)
</script>
