<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A2-OA1 排班管理</h2>
        <div class="desc">排班模板与排班记录闭环：分页检索、姓名化展示、状态流转（草稿→发布→执行/异常）。</div>
      </div>
    </div>

    <el-alert type="info" :closable="false" show-icon>
      <template #title>流程提示</template>
      <div>• 先创建模板，再创建排班；• 支持搜索/筛选/分页；• 排班状态支持发布、执行、异常、重开。</div>
    </el-alert>

    <el-card class="zy-card" style="margin-top: 12px;">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>班次模板</span>
          <el-button type="primary" @click="createTemplate">新建模板</el-button>
        </div>
      </template>

      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="templateQuery.keyword" placeholder="班次名/时间" clearable style="width:220px" @change="loadTemplates"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="templateQuery.status" clearable placeholder="全部" style="width:140px" @change="loadTemplates">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
          </el-select>
        </el-form-item>
        <el-button @click="loadTemplates">查询</el-button>
      </el-form>

      <el-table :data="templates.items" border>
        <el-table-column prop="name" label="班次名称" min-width="150" />
        <el-table-column prop="start_time" label="开始" width="100" />
        <el-table-column prop="end_time" label="结束" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }"><el-tag>{{ statusText(row.status) }}</el-tag></template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="templateQuery.page"
          v-model:page-size="templateQuery.page_size"
          :page-sizes="[10,20,50]"
          layout="total, sizes, prev, pager, next"
          :total="templates.total"
          @change="loadTemplates"
        />
      </div>
    </el-card>

    <el-card class="zy-card" style="margin-top: 12px;">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>排班记录</span>
          <el-button type="primary" @click="createAssignment">新建排班</el-button>
        </div>
      </template>
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="assignmentQuery.keyword" placeholder="班次/人员" clearable style="width:220px" @change="loadAssignments"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="assignmentQuery.status" clearable placeholder="全部" style="width:140px" @change="loadAssignments">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已执行" value="executed" />
            <el-option label="异常" value="exception" />
          </el-select>
        </el-form-item>
        <el-button @click="loadAssignments">查询</el-button>
      </el-form>

      <el-table :data="assignments.items" border>
        <el-table-column prop="duty_date" label="值班日期" width="130" />
        <el-table-column prop="shift_name" label="班次" min-width="140" />
        <el-table-column prop="user_name" label="人员姓名" min-width="120" />
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }"><el-tag>{{ statusText(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" @click="doStatus(row, 'publish')">发布</el-button>
              <el-button link type="success" @click="doStatus(row, 'execute')">执行</el-button>
              <el-button link type="danger" @click="doStatus(row, 'mark_exception')">异常</el-button>
              <el-button link @click="doStatus(row, 'reopen')">重开</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination
          v-model:current-page="assignmentQuery.page"
          v-model:page-size="assignmentQuery.page_size"
          :page-sizes="[10,20,50]"
          layout="total, sizes, prev, pager, next"
          :total="assignments.total"
          @change="loadAssignments"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const templates = reactive<any>({ items: [], total: 0 })
const assignments = reactive<any>({ items: [], total: 0 })

const templateQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const assignmentQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })

const loadTemplates = async () => {
  const resp = await http.get('/oa1-shift/templates', { params: templateQuery })
  Object.assign(templates, resp.data.data || { items: [], total: 0 })
}

const loadAssignments = async () => {
  const resp = await http.get('/oa1-shift/assignments', { params: assignmentQuery })
  Object.assign(assignments, resp.data.data || { items: [], total: 0 })
}

const createTemplate = async () => {
  const form: any = { name: '', start_time: '08:00', end_time: '16:00', status: 'draft' }
  await ElMessageBox.prompt('请输入班次名称', '新建模板', { inputValue: '白班' }).then(async ({ value }) => {
    form.name = value
    await http.post('/oa1-shift/templates', form)
    ElMessage.success('模板已创建')
    await loadTemplates()
  })
}

const createAssignment = async () => {
  if (!templates.items.length) {
    ElMessage.warning('请先创建班次模板')
    return
  }
  const { value } = await ElMessageBox.prompt('请输入值班人员 user_id（可从其他模块复制）', '新建排班')
  const shift = templates.items[0]
  const today = new Date().toISOString().slice(0, 10)
  await http.post('/oa1-shift/assignments', { shift_id: shift.id, user_id: value, duty_date: today, status: 'draft' })
  ElMessage.success('排班已创建')
  await loadAssignments()
}

const doStatus = async (row: any, action: string) => {
  try {
    await http.post(`/oa1-shift/assignments/${row.id}/status`, { action, note: '前端操作' })
    ElMessage.success('状态已更新')
    await loadAssignments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '状态更新失败')
  }
}

const statusText = (s: string) => ({ draft: '草稿', published: '已发布', executed: '已执行', exception: '异常', assigned: '草稿' } as any)[s] || s || '—'

onMounted(async () => {
  await loadTemplates()
  await loadAssignments()
})
</script>
