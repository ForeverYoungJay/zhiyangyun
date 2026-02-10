<template>
  <el-space direction="vertical" fill>
    <el-card>
      <el-form inline>
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address"/></el-form-item>
        <el-button type="primary" @click="create">新增</el-button>
      </el-form>
    </el-card>
    <el-card>
      <el-table :data="rows"><el-table-column prop="code" label="编码"/><el-table-column prop="name" label="名称"/><el-table-column prop="address" label="地址"/></el-table>
    </el-card>
  </el-space>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';import http from '../../api/http';
const rows = ref<any[]>([]); const form = ref({ code: '', name: '', address: '' })
const load = async()=>{ const r = await http.get('/buildings'); rows.value = r.data }
const create = async()=>{ await http.post('/buildings', form.value); form.value={code:'',name:'',address:''}; await load() }
onMounted(load)
</script>
