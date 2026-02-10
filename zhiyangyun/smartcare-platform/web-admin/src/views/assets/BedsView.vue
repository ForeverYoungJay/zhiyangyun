<template>
  <el-space direction="vertical" fill>
    <el-card>
      <el-form inline>
        <el-form-item label="房间ID"><el-input v-model="form.room_id" style="width:260px"/></el-form-item>
        <el-form-item label="床位号"><el-input v-model="form.bed_no"/></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status" style="width:140px"><el-option value="vacant"/><el-option value="occupied"/><el-option value="reserved"/><el-option value="maintenance"/></el-select></el-form-item>
        <el-button type="primary" @click="create">新增</el-button>
      </el-form>
    </el-card>
    <el-card><el-table :data="rows"><el-table-column prop="bed_no" label="床位号"/><el-table-column prop="status" label="状态"/><el-table-column prop="room_id" label="房间ID"/></el-table></el-card>
  </el-space>
</template>
<script setup lang="ts">
import { ref,onMounted } from 'vue';import http from '../../api/http';
const rows=ref<any[]>([]);const form=ref({room_id:'',bed_no:'A',status:'vacant'})
const load=async()=>{rows.value=(await http.get('/beds')).data}
const create=async()=>{await http.post('/beds',form.value);await load()}
onMounted(load)
</script>
