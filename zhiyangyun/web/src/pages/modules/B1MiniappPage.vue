<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>B1 护理员端服务流</h2>
        <div class="desc">小程序服务请求闭环：分页检索、状态筛选、姓名化展示与状态流转通知。</div>
      </div>
      <el-space>
        <el-button @click="load">刷新</el-button>
        <el-button type="primary" @click="drawerVisible = true">新建请求</el-button>
      </el-space>
    </div>

    <el-card class="zy-card">
      <el-form inline>
        <el-form-item label="关键字"><el-input v-model="query.keyword" clearable placeholder="内容/长者姓名/编号" @change="onSearch" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部状态" @change="onSearch" style="width:150px">
            <el-option label="pending" value="pending" />
            <el-option label="accepted" value="accepted" />
            <el-option label="processing" value="processing" />
            <el-option label="completed" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-table :data="rows" border>
        <el-table-column prop="elder_name" label="长者姓名" min-width="120"/>
        <el-table-column prop="elder_no" label="长者编号" min-width="120"/>
        <el-table-column prop="request_type" label="请求类型" min-width="120"/>
        <el-table-column prop="content" label="请求内容" min-width="220"/>
        <el-table-column prop="status" label="状态" min-width="120"/>
        <el-table-column label="操作" width="260">
          <template #default="scope">
            <el-space>
              <el-button size="small" @click="updateStatus(scope.row, 'accepted')">接单</el-button>
              <el-button size="small" @click="updateStatus(scope.row, 'processing')">处理中</el-button>
              <el-button size="small" type="success" @click="updateStatus(scope.row, 'completed')">完成</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @current-change="load" @size-change="load" />
      </div>
    </el-card>

    <el-drawer v-model="drawerVisible" title="新建服务请求" size="520px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="长者"><el-select v-model="form.elder_id" style="width:100%"><el-option v-for="e in elders" :key="e.id" :label="`${e.name}（${e.elder_no || '-'}）`" :value="e.id"/></el-select></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.request_type" style="width:100%"><el-option label="护理服务" value="care"/><el-option label="健康异常" value="health_alert"/><el-option label="生活协助" value="life_help"/></el-select></el-form-item>
        <el-form-item label="内容"><el-input type="textarea" :rows="4" v-model="form.content"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="drawerVisible=false">取消</el-button><el-button type="primary" @click="create">提交</el-button></template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const rows = ref<any[]>([])
const elders = ref<any[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const form = reactive({ elder_id: '', request_type: 'care', content: '' })

const load = async () => {
  const resp = (await http.get('/b1-miniapp/requests', { params: query })).data.data || {}
  rows.value = resp.items || []
  total.value = resp.total || 0
}
const onSearch = async () => { query.page = 1; await load() }
const create = async () => {
  if (!form.elder_id || !form.content) return ElMessage.error('请完整填写')
  await http.post('/b1-miniapp/requests', form)
  drawerVisible.value = false
  form.content = ''
  ElMessage.success('提交成功')
  await load()
}
const updateStatus = async (row: any, status: string) => {
  await http.post(`/b1-miniapp/requests/${row.id}/status`, null, { params: { status } })
  ElMessage.success('状态更新成功')
  await load()
}

onMounted(async () => {
  elders.value = (await http.get('/elders')).data.data || []
  await load()
})
</script>
