<template>
  <el-space direction="vertical" fill>
    <el-card>
      <el-form inline>
        <el-form-item label="楼栋ID"><el-input v-model="form.building_id" style="width:280px"/></el-form-item>
        <el-form-item label="楼层"><el-input-number v-model="form.floor_no" :min="1"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-button type="primary" @click="create">新增</el-button>
      </el-form>
    </el-card>
    <el-card><el-table :data="rows"><el-table-column prop="building_id" label="楼栋ID"/><el-table-column prop="floor_no" label="楼层"/><el-table-column prop="name" label="名称"/></el-table></el-card>
  </el-space>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';import http from '../../api/http';
const rows=ref<any[]>([]);const form=ref({building_id:'',floor_no:1,name:''})
const load=async()=>{rows.value=(await http.get('/floors')).data}
const create=async()=>{await http.post('/floors',form.value);await load()}
onMounted(load)
</script>
