<template>
  <div class="page-shell">
    <div class="page-title"><h2>A2-OA2 审批流</h2></div>
    <el-card class="zy-card">
      <el-form inline>
        <el-form-item label="关键字"><el-input v-model="query.keyword" clearable placeholder="单号/备注/人员" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable style="width:140px"><el-option label="待审" value="pending" /><el-option label="审批中" value="in_review" /><el-option label="通过" value="approved" /><el-option label="驳回" value="rejected" /></el-select>
        </el-form-item>
        <el-form-item label="类型"><el-input v-model="query.module" clearable placeholder="leave/expense" /></el-form-item>
        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="openCreate">新建审批</el-button>
      </el-form>

      <el-table :data="rows.items" border>
        <el-table-column prop="module" label="类型" width="110" />
        <el-table-column prop="biz_id" label="业务单号" min-width="160" />
        <el-table-column prop="applicant_display_name" label="申请人" width="120" />
        <el-table-column prop="approver_display_name" label="审批人" width="120" />
        <el-table-column prop="cc_names" label="抄送" min-width="180"><template #default="{row}">{{ (row.cc_names||[]).join('、') || '-' }}</template></el-table-column>
        <el-table-column prop="current_step" label="进度" width="90"><template #default="{row}">{{ row.current_step }}/{{ row.total_steps }}</template></el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{row}">
            <el-button link type="success" @click="act(row.id, 'approve')">通过</el-button>
            <el-button link type="danger" @click="act(row.id, 'reject')">驳回</el-button>
            <el-button link @click="showLogs(row.id)">轨迹</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" :total="rows.total" @change="load" />
      </div>
    </el-card>

    <el-dialog v-model="createVisible" title="新建审批" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="审批类型"><el-input v-model="form.module" placeholder="leave/expense/purchase" /></el-form-item>
        <el-form-item label="业务单号"><el-input v-model="form.biz_id" /></el-form-item>
        <el-form-item label="审批人">
          <el-select v-model="form.approver_id" filterable>
            <el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="抄送人">
          <el-select v-model="form.cc_user_ids" multiple filterable>
            <el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="总步骤"><el-input-number v-model="form.total_steps" :min="1" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="createVisible=false">取消</el-button><el-button type="primary" @click="create">提交</el-button></template>
    </el-dialog>

    <el-dialog v-model="logVisible" title="审批轨迹" width="560px">
      <el-timeline>
        <el-timeline-item v-for="l in logs" :key="l.id" :timestamp="l.acted_at">{{ l.operator_name }}：{{ l.action }}（{{ l.note || '无备注' }}）</el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const query = reactive({ page: 1, page_size: 10, keyword: '', status: '', module: '' })
const rows = reactive<any>({ items: [], total: 0 })
const users = ref<any[]>([])
const logs = ref<any[]>([])
const logVisible = ref(false)
const createVisible = ref(false)
const form = reactive<any>({ module: 'leave', biz_id: '', approver_id: '', cc_user_ids: [], total_steps: 1, note: '' })

const loadUsers = async () => { users.value = (await http.get('/oa2-approval/users/suggest')).data.data || [] }
const load = async () => { Object.assign(rows, (await http.get('/oa2-approval/requests', { params: query })).data.data || { items: [], total: 0 }) }
const openCreate = async () => { await loadUsers(); createVisible.value = true }
const create = async () => { await http.post('/oa2-approval/requests', form); ElMessage.success('创建成功'); createVisible.value = false; load() }
const act = async (id: string, action: string) => { await http.post(`/oa2-approval/requests/${id}/action`, { action }); ElMessage.success('已处理'); load() }
const showLogs = async (id: string) => { logs.value = (await http.get(`/oa2-approval/requests/${id}/logs`)).data.data || []; logVisible.value = true }

onMounted(load)
</script>