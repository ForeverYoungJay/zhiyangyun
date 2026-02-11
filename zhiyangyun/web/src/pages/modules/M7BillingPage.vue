<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A1-M7 费用管理</h2>
        <div class="desc">展示任务自动扣费结果，支持月度发票补录与核对。</div>
      </div>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="zy-card">
          <template #header>账单明细（含任务自动扣费）</template>
          <el-table :data="items" border>
            <el-table-column prop="elder_id" label="长者"/>
            <el-table-column prop="item_name" label="项目"/>
            <el-table-column prop="amount" label="金额"/>
            <el-table-column prop="charged_on" label="日期"/>
            <el-table-column prop="status" label="状态">
              <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>月度发票</div>
              <div style="font-size:12px;color:#909399">用于补录月账单汇总，便于财务核对自动扣费结果。</div>
            </div>
          </template>
          <el-form inline>
            <el-form-item label="长者ID"><el-input v-model="invoice.elder_id" placeholder="请输入长者ID"/></el-form-item>
            <el-form-item label="账期"><el-input v-model="invoice.period_month" placeholder="YYYY-MM"/></el-form-item>
            <el-form-item label="总额"><el-input-number v-model="invoice.total_amount" :min="0"/></el-form-item>
            <el-button type="primary" @click="createInvoice">新增</el-button>
          </el-form>
          <el-table :data="invoices" border style="margin-top:10px">
            <el-table-column prop="elder_id" label="长者"/>
            <el-table-column prop="period_month" label="月份"/>
            <el-table-column prop="total_amount" label="总额"/>
            <el-table-column prop="paid_amount" label="已付"/>
            <el-table-column prop="status" label="状态">
              <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const items = ref<any[]>([])
const invoices = ref<any[]>([])
const invoice = reactive({ elder_id: '', period_month: new Date().toISOString().slice(0, 7), total_amount: 0 })

const load = async () => {
  items.value = (await http.get('/m7-billing/items')).data.data
  invoices.value = (await http.get('/m7-billing/invoices')).data.data
}

const createInvoice = async () => {
  if (!invoice.elder_id) return ElMessage.error('请填写长者ID')
  await http.post('/m7-billing/invoices', invoice)
  ElMessage.success('发票创建成功')
  await load()
}

const statusTagClass = (status: string) => {
  if (['paid', 'completed'].includes(status)) return 'zy-tag-success'
  if (['pending', 'partial'].includes(status)) return 'zy-tag-warning'
  if (['overdue', 'failed'].includes(status)) return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(load)
</script>
