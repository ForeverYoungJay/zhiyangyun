<template>
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card>
        <template #header>账单明细（含任务自动扣费）</template>
        <el-table :data="items" border>
          <el-table-column prop="elder_id" label="长者"/>
          <el-table-column prop="item_name" label="项目"/>
          <el-table-column prop="amount" label="金额"/>
          <el-table-column prop="charged_on" label="日期"/>
          <el-table-column prop="status" label="状态"/>
        </el-table>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <template #header>月度发票</template>
        <el-form inline>
          <el-form-item><el-input v-model="invoice.elder_id" placeholder="elder_id"/></el-form-item>
          <el-form-item><el-input v-model="invoice.period_month" placeholder="YYYY-MM"/></el-form-item>
          <el-form-item><el-input-number v-model="invoice.total_amount" :min="0"/></el-form-item>
          <el-button type="primary" @click="createInvoice">新增</el-button>
        </el-form>
        <el-table :data="invoices" border style="margin-top:10px">
          <el-table-column prop="elder_id" label="长者"/>
          <el-table-column prop="period_month" label="月份"/>
          <el-table-column prop="total_amount" label="总额"/>
          <el-table-column prop="paid_amount" label="已付"/>
          <el-table-column prop="status" label="状态"/>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import http from '../../api/http'

const items = ref<any[]>([])
const invoices = ref<any[]>([])
const invoice = reactive({ elder_id: '', period_month: new Date().toISOString().slice(0, 7), total_amount: 0 })

const load = async () => {
  items.value = (await http.get('/m7-billing/items')).data.data
  invoices.value = (await http.get('/m7-billing/invoices')).data.data
}

const createInvoice = async () => {
  await http.post('/m7-billing/invoices', invoice)
  await load()
}

onMounted(load)
</script>
