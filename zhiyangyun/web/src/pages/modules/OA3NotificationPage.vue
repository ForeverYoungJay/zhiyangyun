<template>
  <div class="page-shell">
    <div class="page-title"><h2>A2-OA3 通知触达</h2></div>
    <el-card class="zy-card">
      <el-form inline>
        <el-form-item label="关键字"><el-input v-model="query.keyword" clearable placeholder="标题/内容" /></el-form-item>
        <el-form-item label="渠道"><el-select v-model="query.channel" clearable style="width:120px"><el-option label="站内" value="in_app" /><el-option label="短信" value="sms" /><el-option label="邮件" value="email" /></el-select></el-form-item>
        <el-form-item label="状态"><el-select v-model="query.status" clearable style="width:120px"><el-option label="待发" value="pending" /><el-option label="已送达" value="sent" /><el-option label="失败" value="failed" /></el-select></el-form-item>
        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="createVisible = true">新建通知</el-button>
      </el-form>
      <el-table :data="rows.items" border>
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="target_name" label="接收人" width="120" />
        <el-table-column prop="channel" label="渠道" width="100" />
        <el-table-column prop="strategy" label="策略" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="retry_count" label="重试" width="80" />
        <el-table-column label="操作" width="180"><template #default="{row}"><el-button link type="success" @click="act(row.id,'deliver')">送达</el-button><el-button link @click="act(row.id,'retry')">重试</el-button><el-button link type="danger" @click="act(row.id,'fail')">失败</el-button></template></el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px"><el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="rows.total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="load"/></div>
    </el-card>

    <el-dialog v-model="createVisible" title="新建通知" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" /></el-form-item>
        <el-form-item label="渠道"><el-select v-model="form.channel"><el-option label="站内" value="in_app" /><el-option label="短信" value="sms" /><el-option label="邮件" value="email" /></el-select></el-form-item>
        <el-form-item label="触达策略"><el-select v-model="form.strategy"><el-option label="立即发送" value="immediate" /><el-option label="延迟队列" value="queued" /></el-select></el-form-item>
        <el-form-item label="接收范围"><el-select v-model="form.receiver_scope"><el-option label="全员" value="all" /><el-option label="单人" value="single" /></el-select></el-form-item>
        <el-form-item label="目标用户" v-if="form.receiver_scope==='single'"><el-select v-model="form.target_user_id" filterable><el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="createVisible=false">取消</el-button><el-button type="primary" @click="create">提交</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const query = reactive({ page: 1, page_size: 10, keyword: '', status: '', channel: '' })
const rows = reactive<any>({ items: [], total: 0 })
const users = ref<any[]>([])
const createVisible = ref(false)
const form = reactive<any>({ title: '', content: '', channel: 'in_app', receiver_scope: 'all', strategy: 'immediate', target_user_id: '' })

const loadUsers = async () => { users.value = (await http.get('/oa3-notification/users/suggest')).data.data || [] }
const load = async () => { Object.assign(rows, (await http.get('/oa3-notification/messages', { params: query })).data.data || { items: [], total: 0 }) }
const create = async () => { await http.post('/oa3-notification/messages', form); ElMessage.success('发送成功'); createVisible.value = false; load() }
const act = async (id: string, action: string) => { await http.post(`/oa3-notification/messages/${id}/action`, { action }); ElMessage.success('已更新'); load() }

onMounted(async () => { await loadUsers(); await load() })
</script>