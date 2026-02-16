<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A1-M7 费用管理</h2>
        <div class="desc">收费业务闭环：账单生成、核销、异常处理、状态流转与事件追溯。</div>
      </div>
      <el-button @click="loadAll">刷新</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="zy-card">
          <template #header>
            <div>账单明细</div>
          </template>
          <el-form inline>
            <el-form-item label="关键字">
              <el-input v-model="itemQuery.keyword" clearable placeholder="项目/长者姓名/编号" @change="onItemSearch" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="itemQuery.status" clearable placeholder="全部" style="width: 160px" @change="onItemSearch">
                <el-option label="unpaid" value="unpaid" />
                <el-option label="partial" value="partial" />
                <el-option label="paid" value="paid" />
                <el-option label="overdue" value="overdue" />
                <el-option label="waived" value="waived" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-table :data="items" border style="margin-top:8px">
            <el-table-column prop="elder_name" label="长者姓名" min-width="110" />
            <el-table-column prop="elder_no" label="长者编号" min-width="120" />
            <el-table-column prop="item_name" label="项目" min-width="130" />
            <el-table-column prop="amount" label="金额" min-width="90" />
            <el-table-column prop="charged_on" label="日期" min-width="120"/>
            <el-table-column prop="status" label="状态" min-width="100">
              <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination
              v-model:current-page="itemQuery.page"
              v-model:page-size="itemQuery.page_size"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="itemTotal"
              @current-change="loadItems"
              @size-change="onItemSizeChange"
            />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>月度发票</div>
              <div style="font-size:12px;color:#909399">支持账单生成、核销、异常处理（逾期/争议/豁免）及事件追踪。</div>
            </div>
          </template>

          <el-form inline>
            <el-form-item label="关键字"><el-input v-model="invoiceQuery.keyword" clearable placeholder="姓名/编号/账期" @change="onInvoiceSearch" /></el-form-item>
            <el-form-item label="状态">
              <el-select v-model="invoiceQuery.status" clearable placeholder="全部" style="width: 160px" @change="onInvoiceSearch">
                <el-option label="open" value="open" />
                <el-option label="partial" value="partial" />
                <el-option label="paid" value="paid" />
                <el-option label="overdue" value="overdue" />
                <el-option label="disputed" value="disputed" />
                <el-option label="waived" value="waived" />
              </el-select>
            </el-form-item>
          </el-form>

          <el-form inline style="margin-top:8px">
            <el-form-item label="长者">
              <el-autocomplete
                v-model="elderKeyword"
                :fetch-suggestions="queryElders"
                value-key="label"
                placeholder="输入姓名/编号"
                @select="onElderSelect"
                clearable
                style="width: 220px"
              />
            </el-form-item>
            <el-form-item label="账期"><el-input v-model="invoiceForm.period_month" placeholder="YYYY-MM" style="width:120px"/></el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateInvoice">生成账单发票</el-button>
              <el-button @click="createManualInvoice">手工补录</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="invoices" border style="margin-top:10px">
            <el-table-column prop="elder_name" label="长者姓名" min-width="110" />
            <el-table-column prop="elder_no" label="长者编号" min-width="120" />
            <el-table-column prop="period_month" label="账期" min-width="90" />
            <el-table-column prop="total_amount" label="应收" min-width="80" />
            <el-table-column prop="paid_amount" label="已收" min-width="80" />
            <el-table-column prop="unpaid_amount" label="未收" min-width="80" />
            <el-table-column prop="status" label="状态" min-width="100">
              <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="writeoff(scope.row)">核销</el-button>
                <el-dropdown @command="(cmd: string) => exceptionAction(scope.row, cmd)">
                  <span class="el-dropdown-link">异常处理</span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="mark_overdue">标记逾期</el-dropdown-item>
                      <el-dropdown-item command="mark_disputed">标记争议</el-dropdown-item>
                      <el-dropdown-item command="waive">豁免</el-dropdown-item>
                      <el-dropdown-item command="reopen">重开</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button link @click="showEvents(scope.row)">事件</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination
              v-model:current-page="invoiceQuery.page"
              v-model:page-size="invoiceQuery.page_size"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="invoiceTotal"
              @current-change="loadInvoices"
              @size-change="onInvoiceSizeChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-drawer v-model="eventVisible" title="发票事件流水" size="520px">
      <el-timeline>
        <el-timeline-item v-for="x in invoiceEvents" :key="x.id" :timestamp="x.created_at">
          <div><b>{{ x.event_type }}</b> 金额：{{ x.amount }}</div>
          <div style="color:#909399">{{ x.note || '—' }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const items = ref<any[]>([])
const itemTotal = ref(0)
const invoices = ref<any[]>([])
const invoiceTotal = ref(0)
const elderKeyword = ref('')
const eventVisible = ref(false)
const invoiceEvents = ref<any[]>([])

const itemQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const invoiceQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const invoiceForm = reactive({ elder_id: '', period_month: new Date().toISOString().slice(0, 7), total_amount: 0 })

const loadItems = async () => {
  const resp = await http.get('/m7-billing/items', { params: itemQuery })
  const data = resp.data.data || {}
  items.value = data.items || []
  itemTotal.value = data.total || 0
}

const loadInvoices = async () => {
  const resp = await http.get('/m7-billing/invoices', { params: invoiceQuery })
  const data = resp.data.data || {}
  invoices.value = data.items || []
  invoiceTotal.value = data.total || 0
}

const loadAll = async () => {
  await Promise.all([loadItems(), loadInvoices()])
}

const onItemSearch = async () => {
  itemQuery.page = 1
  await loadItems()
}

const onItemSizeChange = async () => {
  itemQuery.page = 1
  await loadItems()
}

const onInvoiceSearch = async () => {
  invoiceQuery.page = 1
  await loadInvoices()
}

const onInvoiceSizeChange = async () => {
  invoiceQuery.page = 1
  await loadInvoices()
}

const queryElders = async (keyword: string, cb: (items: any[]) => void) => {
  const resp = await http.get('/m4-medication/elders/suggest', { params: { keyword, limit: 20 } })
  const list = (resp.data.data || []).map((x: any) => ({ ...x, value: x.id, label: `${x.name}（${x.elder_no}）` }))
  cb(list)
}

const onElderSelect = (item: any) => {
  invoiceForm.elder_id = item.id
  elderKeyword.value = item.label
}

const generateInvoice = async () => {
  if (!invoiceForm.elder_id) return ElMessage.error('请选择长者')
  await http.post('/m7-billing/invoices/generate', { elder_id: invoiceForm.elder_id, period_month: invoiceForm.period_month })
  ElMessage.success('账单发票已生成')
  await loadInvoices()
}

const createManualInvoice = async () => {
  if (!invoiceForm.elder_id) return ElMessage.error('请选择长者')
  await http.post('/m7-billing/invoices', invoiceForm)
  ElMessage.success('手工发票已创建')
  await loadInvoices()
}

const writeoff = async (row: any) => {
  const { value } = await ElMessageBox.prompt(`请输入核销金额（未收：${row.unpaid_amount}）`, '发票核销', { inputValue: `${row.unpaid_amount}` })
  await http.post(`/m7-billing/invoices/${row.id}/writeoff`, { amount: Number(value), note: '前台核销' })
  ElMessage.success('核销成功')
  await loadAll()
}

const exceptionAction = async (row: any, action: string) => {
  await http.post(`/m7-billing/invoices/${row.id}/exception`, { action, note: `前台动作: ${action}` })
  ElMessage.success('异常状态已更新')
  await loadAll()
}

const showEvents = async (row: any) => {
  const resp = await http.get(`/m7-billing/invoices/${row.id}/events`)
  invoiceEvents.value = resp.data.data || []
  eventVisible.value = true
}

const statusTagClass = (status: string) => {
  if (['active', 'completed', 'paid', 'approved', 'admitted'].includes(status)) return 'zy-tag-success'
  if (['pending', 'reserved', 'draft', 'in_progress', 'partial', 'open'].includes(status)) return 'zy-tag-warning'
  if (['failed', 'rejected', 'cancelled', 'discharged', 'stopped', 'overdue', 'disputed', 'waived'].includes(status)) return 'zy-tag-danger'
  return 'zy-tag-info'
}

onMounted(loadAll)
</script>
